from flask import Flask, jsonify, render_template, session, redirect, url_for, send_from_directory, Response, request
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal
from pymavlink import mavutil
import io, cv2, time

app = Flask(__name__)
app.secret_key = 'XHttreAAsdkTTeopOk'

# Connect to the drone
print('Connecting...')
vehicle = connect('udp:localhost:14551')
gnd_speed = 15

# Function to arm and takeoff with altitude
def arm_and_takeoff(altitude):
   while not vehicle.is_armable:
      time.sleep(1)
   print("Arming motors")
   vehicle.mode = VehicleMode("GUIDED")
   vehicle.armed = True
   while not vehicle.armed: time.sleep(1)
   print("Taking Off")
   vehicle.simple_takeoff(altitude)
   while True:
      v_alt = vehicle.location.global_relative_frame.alt
      print(">> Altitude = %.1f m"%v_alt)
      if v_alt >= altitude - 1.0:
          print("Target altitude reached")
          break
      time.sleep(1)

# Function to wait and disarm motor
def disarm():
   while vehicle.armed:
      time.sleep(1)
   vehicle.armed = 'False'

# Function to set velocity and control the drone manually.
def set_velocity_body(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111, #-- BITMASK -> Consider only the velocities
            0, 0, 0,        #-- POSITION
            vx, vy, vz,     #-- VELOCITY
            0, 0, 0,        #-- ACCELERATIONS
            0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

# Function to generate stream from the camera.
def generate_stream():
    # Use (0) instead of the video file to stream the connected camera.
    vc = cv2.VideoCapture('181015_06_FourLevel_15.avi')
    vc.set(cv2.CAP_PROP_BUFFERSIZE, 2)
#    fps = vc.get(cv2.CAP_PROP_FPS)
 #   period = 1000 / fps
    while(vc.isOpened()):
        ret, frame = vc.read()
        if ret:
     #       start_time = time.time()
    #        fc = 0
   #         FPS = 0
  #          processing_time = (time.time() - start_time) * 1000
      #      wait_ms = period - processing_time if period > processing_time else period
       #     if cv2.waitKey(int(wait_ms)) & 0xFF == 27:
        #        break
         #   fc+=1
          #  TIME = time.time() - start_time
          #  FPS = fc / (TIME)
          #  fc = 0
          #  fps_disp = "FPS: "+str(FPS)[:5]
            # You can perform some machine learning algorithms here.
           # image = cv2.putText(frame, fps_disp, (10, 25),
            #    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
            io_buf = io.BytesIO(image_buffer)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')
        else:
            print('Replay Video\n')
            vc.set(cv2.CAP_PROP_POS_FRAMES, 0)
    vc.release()
    cv2.destroyAllWindows()

# The home page
@app.route('/')
def home():
    if 'username' in session:
        return render_template('panel.html')
    else:
        return render_template('index.html')

# Arming motor endpoint
@app.route('/arm', methods=['POST'])
def arm():
    if 'username' in session:
        arm_and_takeoff(10)
        response = jsonify({"armed":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)

# Manual controls end points
@app.route('/up', methods=['POST'])
def up():
    if 'username' in session:
        set_velocity_body(vehicle, gnd_speed, 0, 0)
        response = jsonify({"up":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)
@app.route('/down', methods=['POST'])
def down():
    if 'username' in session:
        set_velocity_body(vehicle, -gnd_speed, 0, 0)
        response = jsonify({"down":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)
@app.route('/left', methods=['POST'])
def left():
    if 'username' in session:
        set_velocity_body(vehicle, 0, -gnd_speed, 0)
        response = jsonify({"left":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)
@app.route('/right', methods=['POST'])
def right():
    if 'username' in session:
        set_velocity_body(vehicle, 0, gnd_speed, 0)
        response = jsonify({"right":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)

# Navigation to address endpoint
@app.route('/navigate', methods=['POST'])
def nav():
    if 'username' in session:
        point2 = LocationGlobalRelative(float(request.args['lon']), float(request.args['lat']), 20)
        vehicle.simple_goto(point2, groundspeed=10)
        response = jsonify({"return":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)

# Land the drone endpoint
@app.route('/land', methods=['POST'])
def land():
    if 'username' in session:
        vehicle.mode = VehicleMode("LAND")
        disarm()
        response = jsonify({"land":"good"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response)
    else:
        return ('', 404)

# Public files
@app.route('/public/<path:path>')
def send_js(path):
    return send_from_directory('public', path)

# Validate user name and password
@app.route('/validate', methods=['POST'])
def validate():
    name = request.form['f1-uName']
    if (name.lower() == 'airpost' and request.form['f1-pswd'] == "789555"):
        session['username'] = 'admin'
        return redirect(url_for('panel'))
    else:
        return render_template('index.html')

# The control panel page
@app.route('/panel')
def panel():
    if 'username' in session:
        return render_template('panel.html')
    else:
        return render_template('index.html')

# Logout page
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template('index.html')
    else:
        return render_template('index.html')

# The video stream endpoint
@app.route('/video_feed')
def video_feed():
    if 'username' in session:
        return Response(
            generate_stream(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:
        return ('', 404)

# The location endpoint
@app.route('/loc', methods=['GET'])
def loc():
#    print(vehicle.attitude)
 #   nextwaypoint=vehicle.commands.next

  #  print (nextwaypoint)
    if 'username' in session:
        try:
            vehicle
        except NameError:
            return ('',400)
        else:
            response = jsonify({"geometry":{"type":"Point","coordinates":[vehicle.location.global_relative_frame.lon,vehicle.location.global_relative_frame.lat]},"type":"Feature","properties":{}})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    else:
        return ('', 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
