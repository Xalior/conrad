import re, datetime
import os.path as op

from cyraxlib.events import events

DATE_RE = re.compile(r'(.*?)(\d+)[/-](\d+)[/-](\d+)[/-](.*)$')


class Post(object):
    @staticmethod
    def check(entry):
        if DATE_RE.search(entry.path):
            return True
        return False

    def __init__(self):
        base, Y, M, D, slug = DATE_RE.search(self.path).groups()
        self.settings.date = datetime.date(int(Y), int(M), int(D))
        self.settings.base = base
        self.settings.slug = op.splitext(slug)[0]

        if not hasattr(self.site, 'posts'):
            self.site.posts = []
        self.site.posts.append(self)
        self.site.posts.sort(key=lambda x: x.date, reverse=True)
        self.site.latest_post = self.site.posts[0]

        for tag in self.settings.get('tags', []):
            tagentries = self.site.tags.setdefault(tag, [])
            if self not in tagentries:
                tagentries.append(self)
                self.site.tags[tag].sort(key=lambda x: x.date, reverse=True)

    def __str__(self):
        return self.slug

    def get_url(self):
        date = self.date.strftime('%Y/%m/%d')
        url = op.join(self.base, date, self.slug) + '/'
        return url


class Page(object):
    @staticmethod
    def check(entry):
        return True

    def __init__(self):
        if self.path.endswith('index.html'):
            self.path = self.path[:-len('index.html')]
        base, slug = op.split(self.path)
        self.settings.base = base
        self.settings.slug = slug

        if not hasattr(self.site, 'pages'):
            self.site.pages = []
        self.site.pages.append(self)

    def __str__(self):
        return self.slug

    def get_url(self):
        url = op.join(self.base, self.slug)
        return url


class Tag(object):
    @staticmethod
    def check(entry):
        return entry.path.startswith('tag/')

    def __init__(self):
        self.slug = self.path[len('tag/'):-len('.html')]
        self.site.tag_cache[self.slug] = self

    def __str__(self):
        return self.slug

    def get_url(self):
        return self.path


def add_taglist_entries(site):
    from cyraxlib.core import Entry
    site.tag_cache = {}
    for tag in site.tags:
        site.entries.append(Entry(site, 'tag/%s.html' % tag, '_taglist.html'))

events.connect('site-traversed', add_taglist_entries)


TYPE_LIST = [Post, Tag, Page]
