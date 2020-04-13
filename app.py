from quart import Quart, request, Response, send_file
from telethon import TelegramClient, utils
import hypercorn.asyncio
import json
import os
import io

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
API_KEY = os.environ.get('API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE THIS TO SOMETHING SECRET')

# Telethon client
client = TelegramClient(API_ID, int(API_ID), API_HASH)
client.parse_mode = 'html'  # <- Render things nicely

# Quart app
app = Quart(__name__)
app.secret_key = SECRET_KEY


# Connect the client before we start serving with Quart
@app.before_serving
async def startup():
    await client.connect()
    await client.start()


# After we're done serving (near shutdown), clean up the client
@app.after_serving
async def cleanup():
    await client.disconnect()


def error(status=505, message=None):
    return Response(json.dumps({'error': message}), status=status, mimetype='application/json')


@app.route('/', methods=['GET'])
async def root():
    return 'ok'


@app.route('/<chat_id>', methods=['POST'])
async def chat_handler(chat_id):
    if API_KEY and request.headers.get('Authorization') != 'Bearer ' + str(API_KEY):
        return error(401, 'not authorized')

    try:
        chat_id = int(chat_id)
    except Exception:
        pass

    form = await request.form
    files = await request.files
    if 'file' not in files:
        return error(400, 'No file')

    file = files['file']
    if file.filename == '':
        return error(400, 'No filename')

    force_document = file.filename.lower().split(".")[-1] not in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', ]
    try:
        entity = await client.get_entity(chat_id)
    except Exception as e:
        raise e
        # return error(400, 'chat_id: ' + str(e))

    try:

        file = await client.upload_file(file.stream, file_name=file.filename)
        message = await client.send_file(entity, file, caption=form.get('caption'), silent=True,
                                         force_document=force_document)
        return Response(json.dumps({'chad_id': chat_id, 'id': message.id}), mimetype='application/json')

    except Exception as e:
        return error(403, f'can not send file: {str(e)}')


@app.route('/<chat_id>/<int:message_id>', methods=['GET', 'DELETE'])
async def message_handler(chat_id, message_id):
    if API_KEY and request.headers.get('Authorization') != 'Bearer ' + str(API_KEY):
        return error(401, 'not authorized')

    try:
        chat_id = int(chat_id)
    except Exception as e:
        pass

    try:
        entity = await client.get_entity(chat_id)
    except Exception as e:
        return error(400, 'chat_id: ' + str(e))

    message_id = int(message_id)

    if request.method == 'GET':

        message = await client.get_messages(entity, ids=message_id)
        if message is None:
            return error(404, f'file {message_id} not found')
        try:
            data = await message.download_media(file=bytes)
        except Exception as e:
            return error(404, f'error to get file {message_id} {str(e)}')

        if message.file.mime_type == 'image/jpeg':
            file_name = f'{chat_id}_{message.id}{message.file.ext}'
        else:
            file_name = f'{chat_id}_{message.id}_{message.file.name}'
        file = io.BytesIO(data)
        return await send_file(file, mimetype=message.file.mime_type, attachment_filename=file_name)

    else:

        try:
            res = await client.delete_messages(entity, message_ids=message_id)
        except Exception as e:
            return error(400, f'error deleting {message_id}: {str(e)}')

        return Response(json.dumps({'status': 'ok'}), mimetype='application/json')


async def main():
    config = hypercorn.Config()
    config.bind = '0.0.0.0:8083'
    await hypercorn.asyncio.serve(app, config)


if __name__ == '__main__':
    client.loop.run_until_complete(main())
