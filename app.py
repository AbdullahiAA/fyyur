#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import dateutil.parser
import babel
from flask import jsonify, render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler

from sqlalchemy import desc
from forms import *
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    main_locations = Venue.query.distinct(Venue.city, Venue.state).all()

    data = []

    for venue in main_locations:

        venue_city = venue.city
        venue_state = venue.state
        venues = []

        venue_data = Venue.query.filter(
            Venue.city == venue_city,
            Venue.state == venue_state
        ).all()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        for this_venue in venue_data:
            venue_id = this_venue.id
            venue_name = this_venue.name
            num_upcoming_shows = Show.query.filter(Show.start_time > current_time).filter(
                Show.venue_id == this_venue.id).count()

            # Append the needed data to venues array
            venues.append({
                'id': venue_id,
                'name': venue_name,
                'num_upcoming_shows': num_upcoming_shows
            })

        # Append the venue data to the data array
        data.append({
            'city': venue_city,
            'state': venue_state,
            'venues': venues  # list of venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form['search_term']

    related_venues = Venue.query.filter(
        db.func.lower(Venue.name).like("%{}%".format(search_term.lower()))).order_by('name').all()

    response = {
        'count': len(related_venues),
        'data': related_venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # TODO: Get the PAST and the UPCOMING shows and append it to the data

    data = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    past_shows = []
    upcoming_shows = []

    for show in shows:
        show_info = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        }

        if str(show.start_time) > current_time:
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    # Appending the show info to the data dictionary
    data.past_shows = past_shows
    data.upcoming_shows = upcoming_shows
    data.past_shows_count = len(past_shows)
    data.upcoming_shows_count = len(upcoming_shows)

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

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        genres = request.form.getlist('genres', type=str)
        facebook_link = request.form['facebook_link']
        website = request.form['website_link']
        seeking_talent = 'seeking_talent' in request.form
        seeking_description = request.form['seeking_description']

        new_venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            genres=genres,
            facebook_link=facebook_link,
            website=website,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )

        db.session.add(new_venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    deletion_status = False

    try:
        venue = Venue.query.get(venue_id)
        shows = Show.query.filter_by(venue_id=venue_id).all()

        for show in shows:
            db.session.delete(show)

        db.session.delete(venue)
        db.session.commit()

        deletion_status = True

        flash("Venue deleted successfully.")

    except:
        deletion_status = False
        db.session.rollback()

    finally:
        db.session.close()
        return jsonify({'status': deletion_status})


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []

    artists = Artist.query.order_by(desc('id')).all()

    for artist in artists:
        # Append the needed information to the data list for each artist
        data.append({
            'id': artist.id,
            'name': artist.name,
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form['search_term']

    related_artists = Artist.query.filter(
        db.func.lower(Artist.name).like("%{}%".format(search_term.lower()))).order_by('name').all()

    response = {
        'count': len(related_artists),
        'data': related_artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    data = Artist.query.get(artist_id)

    past_shows = []
    upcoming_shows = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Fetching the past shows
    raw_past_shows = Show.query.filter(
        Show.start_time < current_time).filter(Show.artist_id == data.id).all()

    for past_show in raw_past_shows:
        venue_data = Venue.query.get(past_show.venue_id)

        venue_name = venue_data.name
        venue_image_link = venue_data.image_link

        past_show_info = {
            "venue_id": past_show.venue_id,
            "venue_name": venue_name,
            "venue_image_link": venue_image_link,
            "start_time": str(past_show.start_time),
        }

        past_shows.append(past_show_info)

    # Fetching the upcoming shows
    raw_upcoming_shows = Show.query.filter(
        Show.start_time > current_time).filter(Show.artist_id == data.id).all()

    for upcoming_show in raw_upcoming_shows:
        venue_data = Venue.query.get(upcoming_show.venue_id)

        venue_name = venue_data.name
        venue_image_link = venue_data.image_link

        upcoming_show_info = {
            "venue_id": upcoming_show.venue_id,
            "venue_name": venue_name,
            "venue_image_link": venue_image_link,
            "start_time": str(upcoming_show.start_time),
        }

        upcoming_shows.append(upcoming_show_info)

    # Appending the show info to the data dictionary
    data.past_shows = past_shows
    data.upcoming_shows = upcoming_shows
    data.past_shows_count = len(past_shows)
    data.upcoming_shows_count = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    # Fetch the actual artist to edit and convert it to a dictionary object
    artist = Artist.query.get(artist_id).__dict__

    artist['website_link'] = artist['website']

    # TODO: populate form with fields from artist with ID <artist_id>
    form = ArtistForm(**artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        artist = Artist.query.get(artist_id)

        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.image_link = request.form['image_link']
        artist.genres = request.form.getlist('genres', type=str)
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website_link']
        artist.seeking_venue = 'seeking_venue' in request.form
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()

        flash('Changes saved successfully')

    except:
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    # Fetch the actual venue to edit and convert it to a dictionary
    venue = Venue.query.get(venue_id).__dict__

    venue['website_link'] = venue['website']

    # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm(**venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        venue = Venue.query.get(venue_id)

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.image_link = request.form['image_link']
        venue.genres = request.form.getlist('genres', type=str)
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website_link']
        venue.seeking_talent = 'seeking_talent' in request.form
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()

        flash('Changes saved successfully')

    except:
        db.session.rollback()

    finally:
        db.session.close()

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

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        image_link = request.form['image_link']
        genres = request.form.getlist('genres', type=str)
        facebook_link = request.form['facebook_link']
        website = request.form['website_link']
        seeking_venue = 'seeking_venue' in request.form
        seeking_description = request.form['seeking_description']

        new_artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            genres=genres,
            facebook_link=facebook_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )

        db.session.add(new_artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + name +
              ' could not be listed.', 'alert-danger')
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    try:
        shows = Show.query.order_by(desc('start_time')).all()

        data = []

        for show in shows:
            venue_data = Venue.query.get(show.venue_id)
            artist_data = Artist.query.get(show.artist_id)

            show_info = {
                "venue_id": show.venue_id,
                "venue_name": venue_data.name,
                "artist_id": show.artist_id,
                "artist_name": artist_data.name,
                "artist_image_link": artist_data.image_link,
                "start_time": str(show.start_time),
            }

            data.append(show_info)
    except:
        flash("Error in fetching the list of shows", 'alert-danger')

    finally:
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

    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        is_artist_id_valid = True
        is_venue_id_valid = True

        if Artist.query.filter(Artist.id == artist_id).count() == 0:
            is_artist_id_valid = False
            raise

        if Venue.query.filter(Venue.id == venue_id).count() == 0:
            is_venue_id_valid = False
            raise

        # Create a new show if there is no error
        new_show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_time=start_time
        )

        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()

        if not is_artist_id_valid:
            flash('Artist ID not found', 'alert-danger')
        elif not is_venue_id_valid:
            flash('Venue ID not found', 'alert-danger')
        else:
            flash('An error occurred. Show could not be listed.', 'alert-danger')
    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
