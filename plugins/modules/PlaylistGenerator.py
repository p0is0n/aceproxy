'''
Playlist Generator
This module can generate .m3u playlists with tv guide
and groups
'''

import re
import urllib2

class PlaylistGenerator(object):

    m3uheader = \
        '#EXTM3U\n'
    m3uemptyheader = '#EXTM3U\n'
    m3uchanneltemplate = \
        '#EXTINF:0 group-title="%s" tvg-name="%s" tvg-logo="%s",%s\n%s\n'
    
    def __init__(self):
        self.itemlist = list()

    def addItem(self, itemdict):
        '''
        Adds item to the list
        itemdict is a dictionary with the following fields:
            name - item name
            url - item URL
            tvg - item JTV name (optional)
            group - item playlist group (optional)
            logo - item logo file name (optional)
        '''
        self.itemlist.append(itemdict)

    @staticmethod
    def _generatem3uline(item):
        '''
        Generates EXTINF line with url
        '''
        return PlaylistGenerator.m3uchanneltemplate % (
            item.get('group', ''), item.get('tvg', ''), item.get('logo', ''),
            item.get('name'), item.get('url'))

    def exportm3u(self, hostport, add_ts=False, empty_header=False, archive=False):
        '''
        Exports m3u playlist
        '''

        ttv2yFile = open('/etc/aceproxy/plugins/ttv2y.txt', "r")
        ttv2ylines = ttv2yFile.readlines()
        ttv2yFile.close()

	ttv2yandex = []

	for line in ttv2ylines:
    	    ttv2yandex_item = line.strip().split(";")
    	    ttv2yandex.append(ttv2yandex_item)
    	
        if not empty_header:
            itemlist = PlaylistGenerator.m3uheader
        else:
            itemlist = PlaylistGenerator.m3uemptyheader

        if add_ts:
                # Adding ts:// after http:// for some players
                hostport = 'ts://' + hostport

        for item in self.itemlist:
            item['tvg'] = item.get('tvg', '') if item.get('tvg') else \
                item.get('name').replace(' ', '_')

            for convert_items in ttv2yandex:
        	if convert_items[0].decode('utf-8') == item.get('name').decode('utf-8'):
		    item['tvg'] = " ".join(str(tmp_str_ttv2y) for tmp_str_ttv2y in convert_items[-1:])
    		    break

            # For .acelive and .torrent
            item['url'] = re.sub('^(http.+)$', lambda match: 'http://' + hostport + '/torrent/' + \
                             urllib2.quote(match.group(0), '') + '/stream.avi', item['url'],
                                   flags=re.MULTILINE)
            # For PIDs
            item['url'] = re.sub('^(acestream://)?(?P<pid>[0-9a-f]{40})$', 'http://' + hostport + '/pid/\\g<pid>/stream.avi',
                                    item['url'], flags=re.MULTILINE)

            itemlist += PlaylistGenerator._generatem3uline(item)

        return itemlist
