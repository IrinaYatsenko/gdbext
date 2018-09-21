# My extensions for gdb

def print_with_lead(str, lead):
  print(" "*lead + str)


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
  
  return base_type.name + '*'*deref_count
 

def get_deref_value(var):
  deref = var
  while is_pointer(deref.type):
    try:
      # might fail if address isn't accessible, e.g. 0x0
      deref = deref.dereference()
    except:
      break

  return deref


def dt_value(var, print_type, lead):
  ''' recursively print out offsets, names, values and types of fields in var '''
  #print('DEBUG: ' + str(var.type.name) + ' at ' + str(lead))
  
  base_type = get_type(var)
  if print_type:
      print_with_lead(base_type + ' at ' + str(var.address), lead)

  if is_pointer(var.type):
      deref = var
      seq = ''
      try:
          while is_pointer(deref.type):
              seq = seq + '->' + str(deref)
              deref = deref.dereference()
          
          print_with_lead(seq, lead)
          dt_value(deref, False, lead)
      except:
          pass
          #print_with_lead(str(deref), lead)
  else:
    if has_fields(var.type): 
      fields = [(f.bitpos, f.name, var[f.name]) for f in var.type.fields()]
      for f in fields:
          print_with_lead('['+hex(f[0])+']'+' : '+f[1]+' : '+str(f[2]), lead)
          dt_value(f[2], True, lead + 2)
    #else:
    #  print_with_lead(str(var), lead)


def dt(var_name):
  frame = gdb.selected_frame()
  var = frame.read_var(var_name)
  dt_value(var, print_type = True, lead = 0)


