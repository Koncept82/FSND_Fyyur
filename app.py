#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://alfgraham@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(ARRAY(db.String()))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.String())
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True, passive_deletes=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True, passive_deletes=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id, ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id, ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for city in cities:
    venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
    data.append({
      "city": city[0],
      "state": city[1],
      "venues": venues_in_city
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in venues:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.venue_id == venue.id)
    for show in shows:
      if (show.start_time > datetime.now()):
        num_upcoming_shows += 1;

    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  list_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []

  for show in list_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    }
    if (show.start_time < datetime.now()):
      past_shows.append(show_add)
    else:
      upcoming_shows.append(show_add)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  print(data, file=sys.stdout.flush())
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm(request.form)

  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash(f'Venue {form.name.data} was successfully listed!')
  except:
    print(sys.exc_info())
      # TODO: on unsuccessful db insert, flash an error instead.
    flash(f'An error occurred. Venue {form.name.data} could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  updated_venue = {
    "name": form.name.data,
    "genres": form.genres.data,
    "address": form.address.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website.data,
    "facebook_link": form.facebook_link.data,
    "seeking_talent": form.seeking_talent.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }

  try:
    db.session.query(Venue).filter(Venue.id == venue_id).update(updated_venue)
    db.session.commit()
    flash(f'Venue {form.name.data} was successfully updated!')
  except: 
    flash(f'An error occurred. Venue {form.name.data} could not be updated')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    flash(f'An error occurred. Venue {venue.name} could not be deleted.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()
    flash(f'Venue {venue.name} was successfully deleted.')
  return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  all_artists = Artist.query.order_by(Artist.name).all()
  data=[]

  for artist in all_artists:
    artist = {
        "id"  : artist.id,
        "name": artist.name
    }
    data.append(artist)
  return render_template('pages/artists.html', artists=data)

#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []

  for artist in artists:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.artist_id == artist.id)
    for show in shows:
      if(show.start_time > datetime.now()):
        num_upcoming_shows += 1;
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })
    response={
      "count": len(artists),
      "data": data
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  past_shows= []
  upcoming_shows = []
  
  for show in list_shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

    show_add = {
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
        }

    if (show.start_time < datetime.now()):
        #print(past_shows, file=sys.stderr)
        past_shows.append(show_add)
    else:
        print(show_add, file=sys.stderr)
        upcoming_shows.append(show_add)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  artist = Artist(
    name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    facebook_link = form.facebook_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash(f'Artist {form.name.data} was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    flash(f'An error occurred. Artist {form.name.data} could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Edit Artsit
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  updated_artist = {
    "name": form.name.data,
    "genres": form.genres.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website.data,
    "facebook_link": form.facebook_link.data,
    "seeking_venue": form.seeking_venue.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }

  try:
    db.session.query(Artist).filter(Artist.id == artist_id).update(updated_artist)
    db.session.commit()
    flash(f'Artist {form.name.data} + was successfully updated!')
  except:
    flash(f'An error occurred. Artist {form.name.data} could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    flash(f'An error occurred. Artist {artist.name} could not be deleted.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()
    flash(f'Artist {artist.name} was successfully deleted.')
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data=[]
  for show in shows:
    show = {
        "venue_id"         : show.venue_id,
        "venue_name"       : Venue.query.get(show.venue_id).name,
        "artist_id"        : show.artist_id,
        "artist_name"      : Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time"       : format_datetime(str(show.start_time))
    }
    data.append(show)
  return render_template('pages/shows.html', shows=data)

#  Add Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()

  try:
    show = Show(
    venue_id=form.venue_id.data,
    artist_id=form.artist_id.data,
    start_time=form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash(f'Show was successfully listed!')
    return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except Exception as e:
    flash(f'An error occurred. Show could not be listed. Error: {e}')
    db.session.rollback()
    return render_template('forms/new_show.html', form=form)
  finally:
    db.session.close()
  return render_template('pages/home.html')

  def upcoming_shows(shows):
    upcoming = []
    for show in shows:
        if start_time_obj(show.start_time) > datetime.now():
            upcoming.append({
                "artist_id"        : show.artist_id,
                "artist_name"      : Artist.query.get(show.artist_id).name,
                "artist_image_link": Artist.query.get(show.artist_id).image_link,
                "start_time"       : format_datetime(str(show.start_time))
            })

    return upcoming


  def upcoming_shows_count(shows):
    return len(upcoming_shows(shows))


  def past_shows(shows):
    past = []
    for show in shows:
        if start_time_obj(show.start_time) < datetime.now():
            past.append({
                "artist_id"        : show.artist_id,
                "artist_name"      : Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time"       : format_datetime(str(show.start_time))
            })

    return past

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
