import falcon
from wdinfo import WdInfo
from logzero import logger

class HtmlTemplate(WdInfo):
    def __init__(self,
                 db = '/home/family/wdinfo.sqlite/wddata.db',
                 ):
        WdInfo.__init__(self, db = db)
        self.html_pre ="""
        <!DOCTYPE html>
        <html>
        <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>
        """
        self.html_suf ="""
        </body>
        </html>
        """

    def table_html(self, head, data):
        ''' giving data with head, output table structure '''
        html_str = '<table border="1"><tr><th>\n'
        res_str = '</th><th>'.join(head)
        html_str = f'{html_str}{res_str}</th></tr>\n'
        for row in data:
            res_str = '</td><td>'.join(row)
            html_str = f'{html_str}<tr><td>{res_str}</td></tr>\n'
        html_str = f'{html_str}</table>\n'
        return html_str

class HelloWorld(HtmlTemplate):
    '''Useful to check if the service is UP!.'''

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_HTML
        resp.body = f"""{self.html_pre}
            <h1>Hello, World!</h1>
            <p>Welcome to Falcon 中文 web framework.</p>
        <a href="status">Status</a>
        {self.html_suf}
        """

class Status(HtmlTemplate):
    '''Useful to check if the service is UP!.'''

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_HTML
        resp.body = self.html_pre
        if self.sqlite_db_exist():
            resp.body = f'{resp.body}<p>Status 1: db exists!</p>\n'
        else:
            resp.body = f'{resp.body}<p>Status (ERROR): db DOES NOT exist!</p>\n'
            return
        # table='src_data'
        table = 'disk1'
        if self.sqlite_table_exist(table=table):
            resp.body = f'{resp.body}<p>Status 2: table exists!</p>\n'
        else:
            resp.body = f'{resp.body}<p>Status (ERROR): table DOES NOT exist!</p>\n{self.html_suf}'
            return
        head, one_rec = self.sqlite_one_record(table=table)
        logger.debug(head)
        if one_rec is None:
            resp.body = f'{resp.body}<p>Status (ERROR): failed to get one record!</p>\n{self.html_suf}'
            return
        else:
            resp.body = f'{resp.body}<p>Status 3: record:</p>\n'
            res_str = self.table_html(head, one_rec)
            resp.body = f'{resp.body}{res_str}</table>\n{self.html_suf}'

class UpdateDb(HtmlTemplate):
    '''Update Database.'''

    def on_get(self, req, resp, sqlite3table, filegroup):
        
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_HTML
        resp.body = self.html_pre
        table = sqlite3table
        filedir = wdfolder.get(filegroup, None)
        prefix = wdprefix.get(filegroup, None)
        resp.body = f'{resp.body}<p>Update table "{sqlite3table}" using file information under folder "{filegroup}"<P>'
        if filedir is None or prefix is None:
            resp.body = f'{resp.body}<p>"{filegroup}" is not in the list of WD!!!<P>'
        else:
            resp.body = f'{resp.body}<p>{filedir=} and {prefix=}<P>'
            self.sqlite_update(table = table,
                           filedir = filedir,
                           prefix = prefix
                           )
            
        resp.body = f'{resp.body}{self.html_suf}\n'

wdfolder = {"wd_music":"/mnt/music",
            "wd_movie":"/mnt/movie",
            "wd_photo":"/mnt/photo",
            "wd_data" :"/mnt/data" ,
            "new_music":"/mnt/public/music",
            "new_movie":"/mnt/public/newmovies",
            "new_photo":"/mnt/public/photos",
            "new_data" :"/mnt/public/data" ,
}
wdprefix = {"wd_music":"/mnt",
            "wd_movie":"/mnt",
            "wd_photo":"/mnt/photo",
            "wd_data" :"/mnt" ,
            "new_music":"/mnt/public",
            "new_movie":"/mnt/public",
            "new_photo":"/mnt/public/photos",
            "new_data" :"/mnt/public" ,
}
app = falcon.App()
app.add_route('/', HelloWorld())
app.add_route('/status', Status())
# Update table with WD filegroup
app.add_route('/{filegroup}/file_info_to_db/{sqlite3table}', UpdateDb())

