from nicegui import app, events, ui
from threading import Thread, Event
import random
import time

app.native.window_args['resizable'] = False
app.native.start_args['debug'] = False

name_list = list()
stop_event = Event()

def rolling():
    while not stop_event.is_set():
        current_name = random.choice(name_list)
        name_show_label.text = current_name
        time.sleep(float(roll_freq.value))
        
def count_down(seconds):
    circle_bar.props('indeterminate=false')
    while seconds > 0 and not stop_event.is_set():
        circle_bar.set_value(seconds / int(count_down_number.value))
        count_down_text.text = f'{seconds} seconds'
        seconds -= 1
        time.sleep(1)
    circle_bar.set_value(0)
    circle_bar.props('indeterminate')
    count_down_text.text = '抽中你了喵！'
    stop()
        
roll_thread = None
count_down_thread = None

def start():
    global roll_thread, count_down_thread, stop_event
    if len(name_list) == 0:
        ui.notify(message='失败喵! 名单为空喵，请先上传名单喵！', type='negative', close_button='OK', progress=True, position='top-right')
        return
    if roll_thread is not None:
        ui.notify(message='失败喵！请先重置喵~', type='warning', close_button='OK', progress=True, position='top-right')
        return
    roll_thread = Thread(target=rolling)
    if radio1.value == 1:
        count_down_thread = Thread(target=count_down, args=(int(count_down_number.value), ))
    stop_event.clear()
    roll_thread.start()
    if radio1.value == 1:
        count_down_thread.start()
    
    
def stop():
    global roll_thread, count_down_thread, stop_event
    if roll_thread is None:
        ui.notify(message='失败喵！请先开始喵~', type='warning', close_button='OK', progress=True, position='top-right')
        return
    stop_event.set()
    roll_thread.join()
    if count_down_thread is not None:
        count_down_thread.join()
    roll_thread = count_down_thread = None
    count_down_text.text = '抽中你了喵！'

def handle_upload(e: events.UploadEventArguments):
    global name_list
    text = e.content.read().decode('utf-8').splitlines()
    for each_name in text:
        nametable.add_rows({'label': each_name})
    name_list = text
    ui.notify(message='上传成功喵！', type='positive', close_button='OK', progress=True, position='top-right')


def reset():
    global stop_event
    name_show_label.text = '???'
    count_down_text.text = 'xx seconds'
    stop_event.clear()
    ui.notify(message='重置成功喵！', type='positive', close_button='OK', progress=True, position='top-right')


# ui.label('app running in native mode')
# ui.button('enlarge', on_click=lambda: app.native.main_window.resize(1000, 700))

with ui.card().classes('w-full items-center justify-center flex flex-col').props('flat bordered'):
    with ui.element('div').classes('row items-center justify-center flex q-gutter-md'):
        ui.icon('extension').classes('text-lg text-weight-bolder')
        ui.label("抽奖小工具（由工口发动机强力驱动）").classes('text-lg text-weight-bolder')

with ui.card().classes('w-full items-center justify-center flex flex-col').props('flat bordered'):
    with ui.element('div').classes('col-14'):
        with ui.circular_progress(size='128px', show_value=False).props('rounded indeterminate show-value') as circle_bar:
            name_show_label = ui.label('???').classes('text-h5 text-weight-bold')
    count_down_text = ui.badge(color='white', text_color='green-14', text='xx seconds').classes('text-lg text-weight-bolder')
    
with ui.element('div').classes('row w-full'):
    with ui.card().props('flat bordered').classes('w-full q-px-none q-pt-none'):
        with ui.element('div').classes('row w-full'):
            ui.button(text='Control Pannel', icon="track_changes").props('flat no-caps text-xl')
            # ui.element('q-space')
            # ui.spinner(type='hourglass', size='1.5rem', color='orange-14').classes('q-ma-sm')
            ui.separator().classes('q-ma-none')
        
        with ui.element('div').classes('row w-full q-gutter-md items-center justify-center'):
            ui.button(text='开始抽奖', icon='play_circle', on_click=start)
            ui.button(text='停止抽奖', icon='stop', on_click=stop)
            ui.button(text='重置抽奖', icon='replay', on_click=reset)
        
        with ui.element('div').classes('row w-full q-gutter-md items-center justify-center'):
            ui.label('运行模式：')
            radio1 = ui.radio({1:'倒计时模式', 2:'手动停止'}, value=1).props('inline')
        
        with ui.element('div').classes('row w-full q-gutter-md items-center justify-center'):
            ui.label('倒计时秒数：')
            count_down_number = ui.number(value='10').props('dense outlined suffix="seconds"')
            ui.label('频率：')
            roll_freq = ui.number(value='0.1', step=0.01).props('dense outlined suffix="seconds"')
        

with ui.element('div').classes('row w-full'):
    with ui.card().props('flat bordered').classes('w-full q-px-none q-pt-none'):
        with ui.element('div').classes('row w-full'):
            ui.button(text='Data Source', icon="description", color='amber-8').props('flat no-caps text-xl')
            # ui.element('q-space')
            # ui.spinner(type='hourglass', size='1.5rem', color='orange-14').classes('q-ma-sm')
            ui.separator().classes('q-ma-none')
        with ui.element('div').classes('row w-full q-px-md justify-center'):
            with ui.element('div').classes('col-6'):
                ui.upload(label="请选择名单源文件(*.txt)并载入", on_upload=handle_upload).props('accept=.txt flat bordered color="amber-6"').classes('max-w-full height: 120px')
            with ui.element('div').classes('col-6'):
                columns = [# {'name': 'class', 'label': 'Class', 'field': 'class', 'required': True, 'align': 'left', 'sortable': True},
                       {'name': 'label', 'label': 'Label', 'field': 'label', 'align': 'left', 'sortable': True},
                       {'name': 'serial', 'label': 'Serial', 'field': 'serial', 'align': 'left', 'sortable': True}]
                nametable = ui.table(columns=columns, rows=[], row_key='class').props('flat bordered dense virtual-scroll').style("height: 120px")
                
if __name__ == '__main__':
    ui.run(favicon='🚀', title='Raffle Tools', reload=False, native=True, window_size=(800, 700), fullscreen=False)
