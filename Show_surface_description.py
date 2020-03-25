"""
Show surface description when the user's mouse hovers over the surface
number in the cell block. Ignore commented surfaces. if the surface was
not found, a warning message pops up.
"""

import sublime
import sublime_plugin
import re


class ShowSurfaceDescription(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        if syntax == 'Packages/User/mcnp.sublime-syntax':
            return True

    @classmethod
    def applies_to_primary_view_only(cls):
        ''' Apply on_hover to all views of file '''
        return False

    def on_hover(self, point: int, hover_zone: int):
        v = self.view
        # get current pos of caret
        cur_pos_row = v.rowcol(point)[0]
        cur_line = sublime.Region(v.text_point(cur_pos_row, 0),
                                  v.text_point(cur_pos_row, 80))
        cell_start = v.rowcol(v.find('Begin Cells', 0).b)[0]
        surf_start = v.rowcol(v.find('Begin Surfaces', 0).b)[0]
        mat_start = v.rowcol(v.find('Begin Materials', 0).b)[0]
        tal_start = v.rowcol(v.find('Begin Tallies', 0).b)[0]
        match_surf = v.match_selector(point, " - (comment.line, \
                                                 storage.type.class.python, \
                                                 entity.name.python, \
                                                 keyword.import, \
                                                 string.quoted.single.ruby, \
                                                 source.python, \
                                                 meta.function.parameters. \
                                                 default-value.python, \
                                                 constant.language.python, \
                                                 variable.language.python)")
        surf_number = v.substr(v.word(point))
        if (match_surf and cell_start <= cur_pos_row <= surf_start and
                surf_number.strip() != ""):
            if (hover_zone != sublime.HOVER_TEXT or v.is_popup_visible()):
                return
            surf_block = sublime.Region(v.text_point(surf_start + 1, 0),
                                        v.text_point(mat_start + 1, 0))
            lines = v.lines(surf_block)
            surf = ""
            for line in lines:
                find_surf = v.find('^' + surf_number, line.a)
                if find_surf and find_surf.a == line.a:
                    surf_num = v.substr(line)[:5].rstrip()
                    surf = v.substr(line)[5:].lstrip()
                    surf_tr = re.search(r'^\d*', surf).group()
                    surf_type = re.search(r'\b(?i)[a-z]/?[a-z]*1?',
                                          surf).group()
                    comment_match = re.search(r'\$.*', surf)
                    if comment_match:
                        comment = comment_match.group()
                    else:
                        comment = ""
                    surf_entr = re.sub(r'\s', '&nbsp;',
                                       surf.lstrip(surf_tr).lstrip().lstrip(
                                           surf_type).rstrip(comment))
                    sp_r = '<span style="color: #FF6347;">'
                    sp_o = '<span style="color: #FFA500;">'
                    sp_g = '<span style="color: #98FB98;">'
                    sp_y = '<span style="color: #F0E68C;">'
                    sp_wh = '<span style="color: DCDCDC; white-space: pre;">'
                    sp_end = '</span>'
                    surf = (sp_o + surf_num + '&nbsp;' + sp_end + sp_y + surf_tr +
                            '&nbsp;&nbsp;' + sp_end + sp_r + surf_type +
                            sp_end + sp_wh + surf_entr + sp_end + sp_g +
                            '&nbsp;&nbsp;' + comment + sp_end)
                    break
                else:
                    surf = '<span style="color:red; background-color: #FFFF00">\
                           <b> &nbsp;Surface was not found. </b> </span>'
            content = ('<body>' + surf + '</body>')
            v.show_popup(content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point,
                         1000, 800, on_navigate=print)

            lines.clear()

        match_mat_hover = v.match_selector(point, "entity.name.python")
        match_mat_re = re.search(r'^\d+', v.substr(cur_line)[5:].lstrip())
        mat_number = v.substr(v.word(point))
        if (match_mat_hover and cell_start <= cur_pos_row <= surf_start and
                mat_number == match_mat_re.group()):
            if (hover_zone != sublime.HOVER_TEXT or v.is_popup_visible()):
                return
            mat_block = sublime.Region(v.text_point(mat_start + 1, 0),
                                        v.text_point(tal_start + 1, 0))
            lines = v.lines(mat_block)
            for line in lines:
                find_mat = v.find(r'^m' + mat_number, line.a)
                if find_mat and find_mat.a == line.a:
                    mat_comment_mantch = re.search(r'\$.*', v.substr(line))
                    if mat_comment_mantch:
                        mat_comment = ('<span style="color: #FFA500;">' +
                                       mat_number + ':&nbsp;&nbsp;</span>' +
                                       '<span style="color: #98FB98;">' +
                                       mat_comment_mantch.group().lstrip('$') +
                                       '</span>')
                    else:
                        mat_comment = "no comment"
                    break
                else:
                    mat_comment = '<span style="color:red; background-color: #FFFF00">\
                        <b> &nbsp;Material was not found. </b> </span>'
            content = ('<body>' + mat_comment + '</body>')
            v.show_popup(content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point,
                         1000, 800, on_navigate=print)

            lines.clear()
                