from flask import request, jsonify, render_template, Response, send_file, send_from_directory, after_this_request
import os
import urllib.request
from werkzeug.utils import secure_filename
import time

from app import app
from camera import VideoCamera, Image

BASE_DIR = os.path.dirname(app.instance_path)

app.config['IMAGE_DIR'] = os.path.join(BASE_DIR, 'app/static/images')
app.config['UPLOAD_DIR'] = os.path.join(BASE_DIR, 'app/storage/images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gen(camera):
    while True:
        frame = camera.get_frame()
        try:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
        except:
            print("Video Ended!!")
            break

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/images/<path:filename>')
def storage(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename, as_attachment=True)


@app.route('/uploadimage', methods=['POST'])
def upload_file():
    file = request.files['image']

    if file and allowed_file(file.filename):
        filename = secure_filename("%s_%s" % (int(time.time()), file.filename))
        file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
        resp = jsonify({'image' : filename})
        resp.status_code = 201
    else:
        resp = jsonify({"message": file.filename + ': File type is not allowed'})
        resp.status_code = 400
    
    return resp


@app.route('/video_feed')
@app.route('/video_feed/<string:video_id>')
def video_feed(video_id=None):
    print("\nVIDEO FEED IS CALLED!\n")    
    return Response(gen(VideoCamera(video_id)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/annotate_image/<string:img_src>')
@app.route('/annotate_image/<string:img_src>/<string:uploaded>')
def annotate_image(img_src, uploaded=False):
    print("\nANNOTATE IMAGE IS CALLED!\n")
    if uploaded:
        path_to_image = os.path.join(app.config['UPLOAD_DIR'], img_src)
        file_handle = open(path_to_image, 'r')
        @after_this_request
        def remove_file(response):
            try:
                os.remove(path_to_image)
                file_handle.close()
            except Exception as error:
                print("Error removing or closing downloaded file handle", error)
            return response
    else:
        path_to_image = os.path.join(app.config['IMAGE_DIR'], img_src)
    return send_file(Image(path_to_image).get_frame(), mimetype='image/jpg')
