# My extensions for gdb

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


def dt_value(var, print_type, depth, depth_limit):
  ''' recursively print out offsets, names, values and types of fields in var '''
  #print('DEBUG: ' + str(var.type.name) + ' at ' + str(depth))
  
  if print_type:
      print_with_lead(get_type(var) + ' at ' + str(var.address), depth)

  if is_pointer(var.type):
      deref = var
      seq = ''
      try:
          while is_pointer(deref.type):
              seq = seq + '->' + str(deref)
              deref = deref.dereference()
          
          print_with_lead(seq, depth)
          dt_value(deref, False, depth, depth_limit)
      except Exception as e:
          #print('DEBUG: ' + str(e))
          pass
  else:
    if has_fields(var.type): 
      # static fields and enums don't affect layout of the type and don't have
      # 'bitpos' property, so let's skip them for now (todo: output them separately?)
      # todo: dump info about base class
      fields = [(f.bitpos, f.name, var[f.name]) for f in var.type.fields() 
                if not f.is_base_class and hasattr(f, 'bitpos')]
      for f in fields:
          print_with_lead('['+hex(f[0])+']'+' '+f[1]+' : '+str(f[2])[:32]+'...', depth)
          if depth < depth_limit:
            dt_value(f[2], True, depth + 1, depth_limit)


def dt(var_name, depth_limit = 1):
  frame = gdb.selected_frame()
  var = frame.read_var(var_name)
  dt_value(var, print_type = True, depth = 0, depth_limit = depth_limit)


