data_holder = {}

def set_data(name, data):
    global data_holder
    data_holder[name] = data

def get_data(name):
    global data_holder
    return data_holder.pop(name, None)
