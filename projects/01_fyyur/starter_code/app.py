#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show, Genre
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
  data = []
  venues = Venue.query.all()
  for venue in venues:
    num_shows = db.session.query(Show).filter_by(venue_id = venue.id).filter(
          Show.start_time > datetime.utcnow().isoformat()).all()
    result = {"city": venue.city, "state": venue.state, "venues": []}
    result["venues"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(num_shows)
    })
    data.append(result)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  searchParam = request.form.get("search_term")
  venues = db.session.query(Venue).with_entities(Venue.id, Venue.name).filter(Venue.name.contains(searchParam)).all()
  for venue in venues:
    num_shows = db.session.query(Show).filter_by(venue_id = venue.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
      
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(num_shows)
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
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  if venue:
    data = venue.__dict__

  shows = db.session.query(Show).filter_by(venue_id = venue.id).filter(
      Show.start_time < datetime.utcnow().isoformat()).all()
  past_shows = []
  for show in shows:
    venue = show.venue
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  new_shows = db.session.query(Show).filter_by(venue_id = venue.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
  upcoming_shows = []
  for show in new_shows:
    venue = show.venue
    upcoming_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)


  return render_template('pages/show_venue.html', venue=data)
  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  new_venue = Venue()
  try:
    venue_genres = request.form.getlist('genres')
    genres = []
    for genre in venue_genres:
      new_genre = Genre(name=genre)
      db.session.add(new_genre)
      db.session.commit()
      genres.append(new_genre)

    new_venue.name = request.form.get('name', '')
    new_venue.city = request.form.get('city', '')
    new_venue.state = request.form.get('state', '')
    new_venue.address = request.form.get('address', '')
    new_venue.phone = request.form.get('phone', '')
    new_venue.genres = genres
    new_venue.facebook_link = request.form.get('facebook_link', '')

    db.session.add(new_venue)
    db.session.commit()
    
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('venues'))
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except Exception as error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    venue = db.session.query(Venue).filter_by(id = venue_id).first()
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_name + ' successfully deleted.')
  except Exception as err:
    flash('An error occurred. Venue with id ' + venue_id + ' could not be deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  data = []
  artists = []

  searchTerm = request.form.get("search_term").lower()
  for artist in db.session.query(Artist).with_entities(Artist.id, Artist.name).all():
    if searchTerm in artist.name.lower():
      artists.append(artist)

  for artist in artists:
    upcoming_shows = db.session.query(Show).filter_by(artist_id = artist.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows)
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

  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  if artist:
    data = artist.__dict__

  shows = db.session.query(Show).filter_by(artist_id = artist.id).filter(
      Show.start_time < datetime.utcnow().isoformat()).all()
  past_shows = []
  for show in shows:
    venue = show.venue
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  new_shows = db.session.query(Show).filter_by(artist_id = artist.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
  upcoming_shows = []
  for show in new_shows:
    venue = show.venue
    upcoming_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistEditForm()
  artist = db.session.query(Artist).filter_by(id = artist_id).first()

  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  form = ArtistEditForm()
  try:
    genres = []
    for genre in request.form.getlist("genres"):
      genres.append(Genre(name=genre))

    artist.name = request.form.get("name")
    artist.city = city
    artist.phone = request.form.get("phone")
    artist.state = state
    artist.facebook_link = request.form.get("facebook_link")
    artist.genres = genres
    artist.image_link = request.form.get("image_link")
    artist.website = request.form.get("website")
    artist.seeking_venue = int(request.form.get("seeking_venue"))
    artist.seeking_description = request.form.get("seeking_description")

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as err:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueEditForm()
  venue = db.session.query(Venue).filter_by(id = venue_id).first()

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueEditForm()  
  venue = Venue.query.get(venue_id)
  try:
    if venue is not None:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.facebook_link = form.facebook_link.data
      db.session.commit()
  except Exception as err:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

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
  form = ArtistForm()
  artist = Artist()

  try:
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.phone = request.form.get('phone', '')
    artist.state = request.form.get('state', '')
    artist.facebook_link = request.form.get('facebook_link', '')

    select_genre = request.form.getlist('genres')
    genres = []
    for genre in select_genre:
      artist_genre = Genre(name=genre)
      db.session.add(artist_genre)
      db.session.commit()
      genres.append(artist_genre)
    artist.genres = genres

    db.session.add(artist)
    db.session.commit()
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = db.session.query(Show).all()
  
  for show in shows:
    show_list = {}
    show_list["venue_id"] = show.venue_id
    show_list["venue_name"] = show.venue.name
    show_list["artist_id"] = show.artist_id
    show_list["artist_name"] = show.artist.name
    show_list["artist_image_link"] = show.artist.image_link
    show_list["start_time"] = show.start_time
    data.append(show_list)
    
  return render_template('pages/shows.html', shows=data)


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
    new_show = Show(
      artist_id = request.form.get("artist_id"),
      venue_id = request.form.get("venue_id"),
      start_time = request.form.get("start_time")
    )
    db.session.add(new_show)
    db.session.commit()

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except Exception as err:
    flash('An error occurred. Show could not be listed.')
  return render_template('pages/home.html')

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
