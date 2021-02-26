import sys
import json
import dateutil.parser
import babel
from flask import (Flask,render_template,request,Response,flash,redirect,url_for
)
from models import (app,db,Venue,Artist,Shows
)
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import (Formatter,FileHandler
)
from flask_wtf import Form
from forms import *
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

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
    #query for venues using the func.count method, then grouping them by city and state
    venues = Venue.query.with_entities (func.count (Venue.id), Venue.city, Venue.state).group_by (Venue.city,
    Venue.state).order_by ('state').all ()
    data = []

    for venue in venues:
        venuesByCity = Venue.query.filter_by (state=venue.state).filter_by (city=venue.city).order_by ('name').all ()
        venueArray = []

        #loop trough each venue in each city
        for each in venuesByCity:
            venueArray.append({
                "id": each.id,
                "name": each.name,
                "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venues_id == each.id).filter
                                          (Shows.start_time > datetime.now()).all())
            })

        #populate data array with the city, state, and the venue array
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": venueArray
        })

    return render_template ('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    searchQuery = request.form.get('search_term')
    query = db.session.query(Venue).filter(Venue.name.ilike(f'%{searchQuery}%')).all()

    data = []

    #iterate through the venues from the query
    for venue in query:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venues_id == venue.id).filter
                                      (Shows.start_time > datetime.now()).all())
        })

    response = {
        "count": len(query),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)

    if not venue:
        return render_template('errors/404.html')

    # filter the venue_id of Shows to where it is equal to the venue_id we need for future shows
    upcomeShowsQuery = db.session.query(Shows).join(Artist).filter(Shows.venues_id == venue_id).filter(
        Shows.start_time > datetime.now()).all()
    upcoming_shows = []

    # filter the venue_id of Shows to where it is equal to the venue_id we need for past shows
    pastShowsQuery = db.session.query(Shows).join(Artist).filter(Shows.venues_id == venue_id).filter(
        Shows.start_time < datetime.now()).all()
    past_shows = []

    # populate array for upcoming and last shows
    for show in pastShowsQuery:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for show in upcomeShowsQuery:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
        }

    return render_template ('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db

    # validation for the seeking talent checkbox
    seeking_talent = True if 'seeking_talent' in request.form else False
    try:
        form = request.form
        venue = Venue(name=form['name'], city=form['city'], state=form['state'], address=form['address'], phone=form['phone'],
                      genres=request.form.getlist('genres'), facebook_link=form['facebook_link'], image_link=form['image_link'],
                      seeking_talent=seeking_talent, past_shows=['past_shows'], upcoming_shows=['upcoming_shows'],
                      past_shows_count=past_shows_count, upcoming_shows_count=upcoming_shows_count)

        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print (sys.exc_info())

    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        venueName = venue.name

        # delete record from the database using db.session.delete
        db.session.delete(venue)
        db.session.commit()
        flash('The venue ' + venueName + ' was successfully deleted!')
    except:
        flash('ERROR: the venue ' + venueName + ' was not deleted!')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect (url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.order_by('name').all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

    #Query search term and use ilike to ensure it is case-insensitive
    searchQuery = request.form.get('search_term')
    query = db.session.query(Artist).filter(Artist.name.ilike(f'%{searchQuery}%')).all()

    data = []
    #iterate trough the artists from the query
    for artist in query:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venues_id == artist.id).filter(
                Shows.start_time > datetime.now()).all()),

        })
    response = {
        "count": len(query),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)

    if not artist:
        return render_template('errors/404.html')

    # filter the artist_id of Shows to where it is equal to the artist_id we need for future shows
    upcomeShowsQuery = db.session.query(Shows).join(Artist).filter(Shows.artist_id == artist_id).filter(
        Shows.start_time > datetime.now()).all()
    upcoming_shows = []

    # filter the artist_id of Shows to where it is equal to the artist_id we need for past shows
    pastShowsQuery = db.session.query(Shows).join(Artist).filter(Shows.artist_id == artist_id).filter(
        Shows.start_time < datetime.now()).all()
    past_shows = []

    # populating array for past shows
    for show in pastShowsQuery:
        past_shows.append({
            "venue_id": show.venues_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    # populating array for upcoming shows
    for show in upcomeShowsQuery:
        upcoming_shows.append({
            "venue_id": show.venues_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "genres": artist.genres,
        "phone": artist.phone,
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

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    artist={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm ()
        artist = Artist.query.get(artist_id)
        name = form.name.data

        artist.name = name
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit ()
        flash ('The artist ' + name + ' has been updated!')
    except:
        db.session.rollback ()
        flash ('ERROR: Could not update artist')
        print (sys.exc_info ())
    finally:
        db.session.close ()

    return redirect (url_for ('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # populate form with values from venue with ID <venue_id>
    venue={
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        name = form.name.data

        venue.name = name
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data

        db.session.commit()
        flash('The venue ' + name + ' has been updated!')
    except:
        db.session.rollback()
        flash ('ERROR: Could not update venue')
        print (sys.exc_info ())
    finally:
        db.session.close ()

    return redirect (url_for ('show_venue', venue_id=venue_id))

#  Create and Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    try:
        form = request.form

        #validation for the seeking venue checkbox
        seeking_venue = True if 'seeking_venue' in request.form else False

        artist = Artist(name=form['name'], city=form['city'], state=form['state'],phone=form['phone'],
                      genres=request.form.getlist('genres'), facebook_link=form['facebook_link'], image_link=form['image_link'],
                       seeking_venue=seeking_venue, seeking_description=form['seeking_description'], past_shows=['past_shows'],
                        upcoming_shows=['upcoming_shows'])
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        # on unsuccessful db insert, flash an error instead.
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print (sys.exc_info())

    finally:
        db.session.close()

    return render_template ('pages/home.html')

@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # use SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        artist = Artist.query.get(artist_id)
        artistName = artist.name

        #delete record from the database using db.session.delete
        db.session.delete(artist)
        db.session.commit()
        flash('The artist ' + artistName + ' was successfully deleted!')
    except:
        flash('ERROR: the artist ' + artistName + ' was not deleted! ')
        db.session.rollback()
        print (sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = db.session.query(Shows).join(Artist).join(Venue).all()
    data = []

    # iterate through shows to populate our data array
    for show in shows:
        data.append({
            "venue_id": show.venues_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    try:
        form = request.form
        show = Shows(artist_id=form['artist_id'], venues_id=form['venue_id'], start_time=form['start_time'])
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
        print (sys.exc_info())

    finally:
        db.session.close()

    return render_template ('pages/home.html')

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
