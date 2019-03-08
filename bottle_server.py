# run 'python bottle_server.py'
# and visit http://localhost:8080/index.html

from bottle import route, get, request, run, template, static_file
import io
import json
import logger
import urllib

@route('/<filepath:path>')
def index(filepath):
    return static_file(filepath, root='.')

@get('/exec')
def get_exec():
  out_s = io.StringIO()

  def json_finalizer(input_code, output_trace):
    ret = dict(code=input_code, trace=output_trace)
    json_output = json.dumps(ret, indent=None)
    out_s.write(json_output)

  logger.exec_script_str(request.query.user_script,
                            request.query.raw_input_json,
                            json_finalizer)
  return out_s.getvalue()


if __name__ == "__main__":
    #run(host='localhost', port=8080, reloader=True)
    run(host='0.0.0.0', port=8003, reloader=True) 
