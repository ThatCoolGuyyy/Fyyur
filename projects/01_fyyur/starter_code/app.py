#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import json
from operator import itemgetter
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from wtforms import BooleanField, PasswordField, TextAreaField, validators, StringField 
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
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

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    Show = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    Show = db.relationship('Show', backref='artist', lazy=True)
    

class Show(db.Model):
  __tablename__ = 'Show'

  show_id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  venue_name = db.Column(db.String())
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  artist_name = db.Column(db.String())
  artist_image_link = db.Column(db.String())
  start_time = db.Column(db.DateTime)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str) :
    date= dateutil.parser.parse(value)
  else:
    date=value 
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
  # def format_datetime(value, format='medium'):
  #   # instead of just date = dateutil.parser.parse(value)
  #   if isinstance(value, str):
  #       date = dateutil.parser.parse(value)
  #   else:
  #       date = value

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
    unique_venues = Venue.query.distinct(Venue.city, Venue.state).all()
    all_venues = Venue.query.all()
    data = []
    now = datetime.now()
    for venue in unique_venues:
        venue_by_city ={
            'city': venue.city,
            'state': venue.state,
            'venues': []
        }
        for venue_data in all_venues:
            if venue.city == venue_data.city and venue.state == venue_data.state:
                venue_by_city['venues'].append({
                    'id': venue_data.id,
                    'name': venue_data.name,
                    'num_upcoming_shows': len(Show.query.filter(Show.start_time > now).filter(Show.venue_id == venue_data.id).all())
                })
        data.append(venue_by_city)
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venue=Venue.query.filter(Venue.name.ilike('%'+request.form.get('search_term')+'%')).all()
  venue_count = len(venue)
  response = {
        "count": venue_count,
        "data": venue
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue=Venue.query.get(venue_id)
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    data= []
    now = datetime.now()
    for show in venue.Show:
      if show.start_time > now:
        upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        })
        upcoming_shows_count += 1
      else:
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        })
        past_shows_count += 1
        data = {
          "id": venue.id,
          "name": venue.name,
          "genres": venue.genres,
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "website": venue.website_link,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": past_shows_count,
          "upcoming_shows_count": upcoming_shows_count,
        }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue_submission():
  form = VenueForm()
  try:
    if form.validate_on_submit:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      address = form.address.data
      image_link = form.image_link.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      seeking_talent = form.seeking_talent.data

      venue = Venue(name=name, genres=genres, address=address, city=city, state=state, phone=phone, website_link=website_link,
      facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description,  image_link=image_link)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
    else:
      flash('error')
      return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
    return redirect(url_for('create_venue_submission'))
  finally:
    db.session.close()
  

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  try:
          venue = Venue.query.filter(venue.id == venue_id).one()
          db.session.delete(venue)
          db.session.commit()
          return redirect(url_for('index'))
  except:
          db.session.rollback()
  finally:
          db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  try:
    data = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)
  except:
    db.session.rollback()
  finally:
    db.session.close()
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist=Artist.query.filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).all()
  count_artists = len(artist)
  response = {
        "count": count_artists,
        "data": artist
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist=Artist.query.get(artist_id)
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in artist.Show:
      if show.start_time > now:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time
        })
        upcoming_shows_count += 1
      else:
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time
        })
        past_shows_count += 1
        data = {
          "id": artist.id,
          "name": artist.name,
          "genres": artist.genres,
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "website": artist.website_link,
          "facebook_link": artist.facebook_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "image_link": artist.image_link,
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": past_shows_count,
          "upcoming_shows_count": upcoming_shows_count,
        }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  if form.validate_on_submit():
    form.populate_obj(artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).one()
  try:
    if form.validate_on_submit:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.address = form.address.data
      artist.image_link = form.image_link.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()    
      flash('Artist ' + request.form['name'] + ' was successfully updated')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      flash('error')
      return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    return redirect(url_for('create_artist_form'))
  finally:
    db.session.close()

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form=VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
   form = VenueForm()
   venue = Venue.query.filter_by(id=venue_id).one()
   try:
      if form.validate_on_submit:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.address = form.address.data
        venue.image_link = form.image_link.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.website_link = form.website_link.data
        venue.seeking_venue = form.seeking_venue.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()    
        flash('Venue ' + request.form['name'] + ' was successfully updated')
        return redirect(url_for('show_venue', venue_id=venue_id))
      else:
        flash('error')
        return render_template('pages/home.html')
   except Exception as error:
     print(error)
   finally:
      db.session.close()
      
    #  Create Artist
    #  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
    if form.validate_on_submit:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      address = form.address.data
      image_link = form.image_link.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      artist = Artist(name=name, genres=genres, address=address, city=city, state=state, phone=phone, website_link=website_link,
      facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description,  image_link=image_link)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
    else:
      flash('error')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      return redirect(url_for('create_venue_form'))
  finally:
    db.session.close()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
   shows = Show.query.all()
   data = []
   for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
   return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  try:
    if form.validate_on_submit:
      venue_id = form.venue_id.data
      artist_id = form.artist_id.data
      start_time = form.start_time.data
      show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
      flash('Show '  + ' was successfully listed!')
      return redirect(url_for('index'))
    else:
      flash('error' + ' was not successfully listed!')
      return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('error' + ' was not successfully listed!')
    return redirect(url_for('index'))
  finally:
    db.session.close()

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
