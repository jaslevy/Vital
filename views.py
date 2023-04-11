import flask
import html
import psycopg2
import sys
import app.database as database

app = flask.Flask("__name__")

@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index():
    html_code = flask.render_template("index.html", modal=False, locations=database.get_building_dict(1, 1, 1),
                                      mp_checked=1, condom_checked=1, aed_checked=1)
    response = flask.make_response(html_code)
    return response

@app.route("/updatempquantity", methods=['POST'])
def update_mp_quantity():

    update_tampons = flask.request.form['update_tampons']
    update_pads = flask.request.form['update_pads']
    location_id = flask.request.form['location_id']

    assert location_id.isdigit(), 'non-integer location id'

    if update_tampons == 'Update tampon quantity' and update_pads == 'Update pad quantity':
        # modal pop up saying you didn't change anything
        return

    new_tampon_quantity = "None"
    new_pad_quantity = "None"
    new_condom_quantity = "None"
    
    if (update_tampons != 'Update quantity of tampons'):
        assert update_tampons[0].isdigit(
        ) and int(update_tampons[0]) >= 0, 'invalid value entered for tampons'
        new_tampon_quantity = int(update_tampons[0])
    if (update_pads != 'Update quantity of pads'):
        assert update_pads[0].isdigit() and int(
            update_pads[0]) >= 0, 'invalid value entered for pads'
        new_pad_quantity = int(update_pads[0])

    try:
        database.update_quantities(location_id,
                                    new_tampon_quantity,
                                    new_pad_quantity,
                                    new_condom_quantity)
        locations = database.get_building_dict(1, 1, 1)
        response =  flask.render_template("index.html", modal=True,
        locations=locations, mp_checked=1, condom_checked=1, aed_checked=1)
        return response
    except Exception as ex:
        html_code = flask.render_template('insertion_error.html')
        response = flask.make_response(html_code)
        print(ex, file=sys.stderr)
        sys.exit(2)

@app.route("/updatecondomquantity", methods=['POST'])
def update_condom_quantity():

    update_condoms = flask.request.form['update_condoms']
    location_id = flask.request.form['location_id']

    print(location_id)
    assert location_id.isdigit(), 'non-integer location id'

    new_tampon_quantity = "None"
    new_pad_quantity = "None"
    new_condom_quantity = "None"
    
    if (update_condoms != 'Update quantity of condoms'):
        assert update_condoms[0].isdigit() and int(
            update_condoms[0]) >= 0, 'invalid value entered for condoms'
        new_condom_quantity = int(update_condoms[0])

    try:
        database.update_quantities(location_id,
                                    new_tampon_quantity,
                                    new_pad_quantity,
                                    new_condom_quantity)
        locations = database.get_building_dict(1, 1, 1)
        response =  flask.render_template("index.html", modal=True,
        locations=locations, mp_checked=1, condom_checked=1, aed_checked=1)
        return response
    except Exception as ex:
        html_code = flask.render_template('insertion_error.html')
        response = flask.make_response(html_code)
        print(ex, file=sys.stderr)
        sys.exit(2)



@app.route("/filter", methods=['GET'])
def show_filters():
    mp = (1 if flask.request.args.get('menstrual_products') == 'on' else 0)
    condom = (1 if flask.request.args.get('condoms') == 'on' else 0)
    aed = (1 if flask.request.args.get('aeds') == 'on' else 0)

    locations = database.get_building_dict(mp, condom, aed)
    return flask.render_template("index.html",
        locations=locations, mp_checked=mp, condom_checked=condom, aed_checked=aed)

# ADD RETURN BUTTON FOR THESE PAGES
@app.route("/contact", methods=['GET'])
def show_contactPage():
   return flask.render_template("contact.html")

@app.route("/about", methods=['GET'])
def show_aboutPage():
   return flask.render_template("about.html")
