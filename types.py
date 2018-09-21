# Extensions for gdb that dump types
import gdb
import re

def print_with_lead(val, lead, spaces_per_lead = 2):
    print(" " * lead * spaces_per_lead + str(val))


def is_pointer(var_type):
    return var_type.code == gdb.TYPE_CODE_PTR


def has_fields(var_type):
    return var_type.code == gdb.TYPE_CODE_STRUCT


def get_type(var):
    base_type = var.type
    deref_count = 0
    
    while is_pointer(base_type):
        deref_count += 1
        base_type = base_type.target()
  
    return str(base_type.name) + '*'*deref_count


def get_deref_value(var):
    deref = var
    while is_pointer(deref.type):
        try:
            # might fail if address isn't accessible, e.g. 0x0
            deref = deref.dereference()
        except:
            break

    return deref


def dt_value(var, depth, filter, depth_limit, print_type_name):
    #print('DEBUG: ' + str(var.type.name) + ' at ' + str(depth))
    
    if print_type_name:
        print_with_lead(get_type(var) + ' at ' + str(var.address), depth)

    if is_pointer(var.type):
        deref = var
        seq = ''
        try:
            while is_pointer(deref.type):
                seq = seq + '->' + str(deref)
                deref = deref.dereference()
            
            print_with_lead(seq, depth)
            dt_value(deref, depth, filter, depth_limit, print_type_name = False)
        except Exception as e:
            #print('DEBUG: ' + str(e))
            pass
    else:
        if has_fields(var.type): 
            # static fields and enums don't affect layout of the type and don't have
            # 'bitpos' property, so let's skip them for now (todo: output them separately?)
            # todo: dump info about base class
            interesting_fields = [(f.bitpos, f.name, var[f.name]) for f in var.type.fields()
                        if not f.is_base_class and hasattr(f, 'bitpos') 
                            and (depth > 0 or filter.match(f.name))]
            for f in interesting_fields:
                print_with_lead('['+hex(f[0])+']'+' '+f[1]+' : '+str(f[2])[:32]+'...', depth)
                if depth < depth_limit:
                    dt_value(f[2], depth + 1, filter, depth_limit, print_type_name = True)


def dt(var_name, depth_limit = 1, filter = ''):
    ''' Recursively print out offsets, names, values and types of fields in var_name,
        which can be name of any variable in the current frame.

        depth_limit: limits recursion into the fields
        filter: regex string to show only matching fields at the top level
    '''
    frame = gdb.selected_frame()
    var = frame.read_var(var_name)
    dt_value(
        var, 
        depth = 0, 
        filter = re.compile(filter),
        depth_limit = depth_limit, 
        print_type_name = True)

def dtv(val, depth_limit = 1, filter = ''):
    ''' Recursively print out offsets, names, values and types of fields in val,
        which must be a gdb.Value type.

        depth_limit: limits recursion into the fields
        filter: regex string to show only matching fields at the top level
    '''
    dt_value(
        val, 
        depth = 0, 
        filter = re.compile(filter),
        depth_limit = depth_limit, 
        print_type_name = True)
