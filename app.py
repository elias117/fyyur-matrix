# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

# Done: connect to a local postgresql database
migrate = Migrate(app, db)
# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Done: implement any missing fields, as a database migration using
    # Flask-Migrate
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(250))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.split(','),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.looking_for_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link
        }

    def find_num_upcoming_shows(self):
        numShows = Show.query.filter(
            Show.venue_id == self.id,
            Show.datetime > datetime.datetime.now()).count()
        return numShows

    def find_num_past_shows(self):
        numShows = Show.query.filter(
            Show.venue_id == self.id,
            Show.datetime < datetime.datetime.now()).count()
        return numShows


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate
    website_link = db.Column(db.String(500))
    looking_for_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def find_num_upcoming_shows(self):
        numShows = Show.query.filter(
            Show.artist_id == self.id,
            Show.datetime > datetime.datetime.now()).count()
        return numShows

    def find_num_past_shows(self):
        numShows = Show.query.filter(
            Show.artist_id == self.id,
            Show.datetime < datetime.datetime.now()).count()
        return numShows

    def format(self):
        return {
            "id": self.id,
            "genres": self.genres.split(','),
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "seeking_venue": self.looking_for_venue,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website_link": self.website_link,
        }

    def find_upcoming_shows(self):
        return Show.query.filter(
            self.id == Show.artist_id,
            Show.datetime > datetime.datetime.now()).all()

    def find_past_shows(self):
        return Show.query.filter(
            self.id == Show.artist_id,
            Show.datetime < datetime.datetime.now()).all()


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'),
        nullable=False)


# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming
    # shows per venue.
    cities_and_states = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []
    for cs in cities_and_states:
        venues_in_city_and_state = Venue.query.filter(
            Venue.city == cs.city, Venue.state == cs.state).all()
        formatted_venues = [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.filter(
                    Show.venue_id == venue.id,
                    Show.datetime > datetime.datetime.now()).count()} for venue in venues_in_city_and_state]
        data.append({
            "city": cs.city,
            "state": cs.state,
            "venues": formatted_venues
        })
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    search_term = request.form.get("search_term", None)
    if search_term is None:
        abort(404)
    found_results = Venue.query.filter(
        Venue.name.ilike(
            "%{}%".format(search_term))).all()
    data = []
    for venue in found_results:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.find_num_upcoming_shows()
        })
    count = len(found_results)
    response = {
        "count": count,
        "data": data
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_term,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    found_venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if found_venue is None:
        abort(404)
    data = found_venue.format()
    past_shows = Show.query.filter(
        Show.venue_id == found_venue.id,
        Show.datetime < datetime.datetime.now()).all()
    upcoming_shows = Show.query.filter(
        Show.venue_id == found_venue.id,
        Show.datetime > datetime.datetime.now()).all()
    format_past_shows = [{"artist_id": show.artist.id,
                          "artist_name": show.artist.name,
                          "artist_image_link": show.artist.image_link,
                          "start_time": str(show.datetime)} for show in past_shows]
    format_upcoming_shows = [{"artist_id": show.artist.id,
                              "artist_name": show.artist.name,
                              "artist_image_link": show.artist.image_link,
                              "start_time": str(show.datetime)} for show in upcoming_shows]
    num_of_upcoming_shows = len(upcoming_shows)
    num_of_past_shows = len(past_shows)

    data["past_shows"] = format_past_shows
    data["upcoming_shows"] = format_upcoming_shows
    data["past_shows_count"] = num_of_past_shows
    data["upcoming_shows_count"] = num_of_upcoming_shows
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=",".join(form.genres.data),
                website_link=form.website_link.data,
                looking_for_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                "Venue " +
                request.form["name"] +
                " was successfully listed!")
            return render_template("pages/home.html")
        except BaseException:
            flash(
                "An error occurred. Venue {} could not be listed".format(
                    form.name.data))
    return render_template('forms/new_venue.html', form=form)


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    venue_to_delete = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if not venue_to_delete:
        abort(404)
    db.session.delete(venue_to_delete)
    db.session.commit()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [
    #     {
    #         "id": 4,
    #         "name": "Guns N Petals",
    #     },
    #     {
    #         "id": 5,
    #         "name": "Matt Quevedo",
    #     },
    #     {
    #         "id": 6,
    #         "name": "The Wild Sax Band",
    #     },
    # ]
    artists = Artist.query.order_by(Artist.id).all()
    if len(artists) == 0:
        abort(404)
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term", "")
    if search_term == "":
        abort(404)

    search_results = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()

    count = len(search_results)
    data = [{"id": artist.id, "name": artist.name, "num_upcoming_shows":
             artist.find_num_upcoming_shows()} for artist in search_results]
    response = {
        "count": count,
        "data": data
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_term,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using
    # artist_id
    found_artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    if not found_artist:
        abort(404)
    data = found_artist.format()
    data["upcoming_shows"] = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(
                show.start_stime)} for show in found_artist.find_upcoming_shows()]
    data["past_shows"] = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(
                show.datetime)} for show in found_artist.find_past_shows()]
    data["past_shows_count"] = len(data["upcoming_shows"])
    data["upcoming_shows_count"] = len(data["past_shows"])
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    if not artist:
        abort(404)
    form.name.data = artist.name
    form.genres.data = artist.genres.split(',')
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link.data
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.looking_for_venue
    form.seeking_description.data = artist.seeking_description
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    if not artist:
        abort(404)
    form = ArtistForm(request.form)
    if form.validate():
        artist.name = form.name.data
        artist.genres = form.name.data.join(",")
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.looking_for_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.add(artist)
        db.session.commit()
        flash(f"Artist {artist.name} has been edited")
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": [
            "Jazz",
            "Reggae",
            "Swing",
            "Classical",
            "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=",".join(form.genres.data),
                website_link=form.website_link.data,
                looking_for_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data)
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                "Artist " +
                request.form["name"] +
                " was successfully listed!")
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
            # listed.')
            return render_template("pages/home.html")
        except BaseException:
            flash(
                "An error occurred. Artist {} could not be listed.".format(
                    form.name.data))
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # data = [{"venue_id": 1,
    #          "venue_name": "The Musical Hop",
    #          "artist_id": 4,
    #          "artist_name": "Guns N Petals",
    #          "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #          "start_time": "2019-05-21T21:30:00.000Z",
    #          },
    #         {"venue_id": 3,
    #          "venue_name": "Park Square Live Music & Coffee",
    #          "artist_id": 5,
    #          "artist_name": "Matt Quevedo",
    #          "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #          "start_time": "2019-06-15T23:00:00.000Z",
    #          },
    #         {"venue_id": 3,
    #          "venue_name": "Park Square Live Music & Coffee",
    #          "artist_id": 6,
    #          "artist_name": "The Wild Sax Band",
    #          "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #          "start_time": "2035-04-01T20:00:00.000Z",
    #          },
    #         {"venue_id": 3,
    #          "venue_name": "Park Square Live Music & Coffee",
    #          "artist_id": 6,
    #          "artist_name": "The Wild Sax Band",
    #          "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #          "start_time": "2035-04-08T20:00:00.000Z",
    #          },
    #         {"venue_id": 3,
    #          "venue_name": "Park Square Live Music & Coffee",
    #          "artist_id": 6,
    #          "artist_name": "The Wild Sax Band",
    #          "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #          "start_time": "2035-04-15T20:00:00.000Z",
    #          },
    #         ]
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.datetime)
        })
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    if form.validate():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                datetime=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        except BaseException:
            flash("An error occurred. Show could not be listed.")
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
