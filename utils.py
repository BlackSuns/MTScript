from configparser import ConfigParser

import arrow


def print_log(message, m_type='INFO'):
    m_types = ('INFO', 'WARNING', 'ERROR')
    prefix = '[ {} ]'.format(arrow.now().format('YYYY-MM-DD HH:mm:ss:SSS'))
    if str(m_type).upper() in m_types:
        m_type = str(m_type).upper()
    else:
        raise RuntimeError('Invalid log type: {}'.format(m_type))

    print('{} -{}- {}'.format(prefix, m_type, message))


# section: section name
# args: a dict for { key: type }
# type should be in ["string", "int", "float", "boolean"]
# type not in these values should be treated as string
def get_config(config_path, section, args):
    config = ConfigParser()
    config.read(config_path)

    if not isinstance(args, dict):
        return None

    if config.has_section(section):
        dictdata = {}
        for arg, argtype in args.items():
            try:
                if argtype == 'int':
                    dictdata[arg] = config.getint(section, arg)
                elif argtype == 'float':
                    dictdata[arg] = config.getfloat(section, arg)
                elif argtype == 'boolean':
                    dictdata[arg] = config.getboolean(section, arg)
                else:
                    dictdata[arg] = config.get(section, arg)
            except:
                dictdata[arg] = None

        return dictdata
    else:
        return None
