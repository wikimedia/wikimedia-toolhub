# This file is part of the Toolhub OAuth client demo application.
#
# Copyright (C) 2021 Bryan Davis and contributors
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
from authlib.integrations.flask_client import OAuth

import flask


app = flask.Flask(__name__)
app.config.from_object("config")


oauth = OAuth(app)
oauth.register(name="toolhub")


@app.route("/")
def index():
    """Home screen."""
    ctx = {
        "profile": None,
    }
    if "token" in flask.session:
        resp = oauth.toolhub.get("user/", token=flask.session["token"])
        resp.raise_for_status()
        ctx["profile"] = resp.json()
    return flask.render_template("home.html", **ctx)


@app.route("/login")
def login():
    """Initiate OAuth handshake with Toolhub."""
    redirect_uri = flask.url_for("authorize", _external=True)
    return oauth.toolhub.authorize_redirect(redirect_uri)


@app.route("/authorize")
def authorize():
    """Handle OAuth callback from Toolhub."""
    flask.session["token"] = oauth.toolhub.authorize_access_token()
    return flask.redirect("/")


@app.route("/logout")
def logout():
    """Clear session and redirect to /."""
    flask.session.clear()
    return flask.redirect("/")
