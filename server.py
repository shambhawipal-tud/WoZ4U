from flask import Flask, render_template, Response, url_for, request, send_file, abort, send_from_directory

import yaml
import time

import qi
from naoqi import ALProxy


app = Flask(__name__)

@app.route('/')
def index():
    try:
        global qi_session
        if qi_session is not None:
            print("Reconnect")
            global ip
            print(ip)
            return render_template("index.html", config=config, reconnect=True, reconnect_ip=ip)
    except NameError:
        return render_template('index.html', config=config, reconnect=False)

@app.route("/connect_robot")
def connect_robot():
    global ip
    ip = request.args.get('ip', type=str)
    port = 9559


    global qi_session
    qi_session = qi.Session()
    
    try:
        qi_session.connect(str("tcp://" + str(ip) + ":" + str(port)))
    except RuntimeError as msg:
        print("qi session connect error!:")
        print(msg)
    
    tts_srv = qi_session.service("ALTextToSpeech")
    tts_srv.setVolume(0.02)
    tts_srv.say("Connected")
    volume_lvl = tts_srv.getVolume()
    voice_pitch = tts_srv.getParameter("pitchShift")
    voice_pitch = round(voice_pitch, 3)

    al_srv = qi_session.service("ALAutonomousLife")
    autonomous_state = al_srv.getState()

    ba_srv = qi_session.service("ALBasicAwareness")
    engagement_state = ba_srv.getEngagementMode()
    ba_runnning = ba_srv.isRunning()

    ab_srv = qi_session.service("ALAutonomousBlinking")
    blinking_enabled = ab_srv.isEnabled()

    motion_srv = qi_session.service("ALMotion")
    orthogonal_collision = motion_srv.getOrthogonalSecurityDistance()
    orthogonal_collision = round(orthogonal_collision, 3)

    tangential_collision = motion_srv.getTangentialSecurityDistance()
    tangential_collision = round(tangential_collision, 3)

    body_breathing = motion_srv.getBreathEnabled("Body")
    legs_breathing = motion_srv.getBreathEnabled("Legs")
    arms_breathing = motion_srv.getBreathEnabled("Arms")
    head_breathing = motion_srv.getBreathEnabled("Head")

    return {
        "status": "ok",
        "ip": ip,
        "autonomous_state": autonomous_state,
        "engagement_state": engagement_state,
        "ba_is_running": ba_runnning,
        "blinking_enabled": blinking_enabled,
        "orthogonal_collision": orthogonal_collision,
        "tangential_collision": tangential_collision,
        "head_breathing": head_breathing,
        "arms_breathing": arms_breathing,
        "body_breathing": body_breathing,
        "legs_breathing": legs_breathing,
        "volume_lvl": volume_lvl,
        "voice_pitch": voice_pitch
    }

@app.route("/set_autonomous_state")
def set_autonomous_state():
    state = request.args.get('state', type=str)
    print(state)

    # TODO: set State
    time.sleep(2)

    return {
       "status": "ok",
       "state": state 
    }

@app.route("/toggle_setting")
def toggle_setting():
    setting = request.args.get('setting', type=str)
    print(setting)

    # TODO: toggle setting
    time.sleep(2)

    return {
       "status": "ok",
       "setting": setting,
        # TODO: return state
    }

@app.route("/say_text")
def say_text():
    msg = request.args.get('msg', type=str)
    print(msg)

    tts = qi_session.service("ALTextToSpeech")
    tts.say(msg)

    return {
       "status": "ok",
       "text": msg,
    }

@app.route("/play_audio")
def play_audio():
    index = request.args.get('index', type=str)
    print(index)

    # TODO: get audio file path
    path = "some/path"

    # TODO: Play the audio
    time.sleep(2)

    return {
       "status": "ok",
       "index": index, 
       "audio_file": path,
    }

@app.route("/show_img/<img_name>")
def show_img(img_name):
    
    # TODO: get img file path
    path = "https://apod.nasa.gov/apod/image/2009/StMiMo_Hudson_960.jpg"

    tablet_srv = qi_session.service("ALTabletService")
    # tablet_srv.showImage(path)
    tablet_srv.showWebview("http://130.239.183.189:5000/show_img_page/example.jpg")

    return {
        # TODO: Return the prev index so that we can reset the button
       "status": "ok",
       "image": path,
    }

@app.route("/set_engagement_state")
def set_engagement_state():
    state = request.args.get('state', type=str)
    print(state)

    # TODO: set State
    time.sleep(2)

    return {
       "status": "ok",
       "engagement_state": state 
    }

@app.route("/serve_image/<img_name>")
def serve_image(img_name):
    try:
        return send_from_directory("static/imgs/", filename=img_name)
    except FileNotFoundError:
        abort(404)

@app.route("/show_img_page/<img_name>")
def show_img_page(img_name):
    img_path = "/static/imgs/" + img_name

    print(img_path)

    time.sleep(2)

    # tablet_srv = qi_session.service("ALTabletService")
    # tablet_srv.showImage("http://130.239.183.189:5000/static/imgs/example.jpg")
    # tablet_srv.showWebview("http://130.239.183.189:5000/show_img_page/example.jpg")

    return render_template("img_view.html", img_src=img_path)  # WORKS! 

    #return {
    #    "status": "ok"
    #}

if __name__ == '__main__':

    global config
    with open("config.yaml", "r") as f:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        config = yaml.safe_load(f)
        print(config)

    app.run(host='0.0.0.0', debug=True)