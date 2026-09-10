import wx
import webbrowser
import copy


class ConfigDialog(wx.Dialog):
    """Minimal first-run setup dialog.

    The desktop GUI only configures the language and the WebUI endpoint.
    TeamTalk server settings are intentionally managed from the WebUI.
    """

    def __init__(self, parent, title, defaults):
        super().__init__(parent, title=title, size=(520, 300))

        self.config_data = copy.deepcopy(defaults)
        webui_defaults = defaults.get('WebUI', {})
        self.language_choice_values = ['pt_BR', 'en']

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(rows=0, cols=2, vgap=10, hgap=10)
        grid.AddGrowableCol(1, 1)

        # Language
        grid.Add(wx.StaticText(panel, label='Language:'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.language = wx.Choice(panel, choices=['Português (Brasil)', 'English'])
        current_lang = defaults.get('Bot', {}).get('language', defaults.get('language', 'pt_BR'))
        try:
            self.language.SetSelection(self.language_choice_values.index(current_lang))
        except ValueError:
            self.language.SetSelection(0)
        grid.Add(self.language, 1, wx.EXPAND)

        # WebUI endpoint
        grid.Add(wx.StaticText(panel, label='WebUI Address:'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.webui_host = wx.TextCtrl(panel, value=str(webui_defaults.get('host', '127.0.0.1')))
        grid.Add(self.webui_host, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label='WebUI Port:'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.webui_port = wx.TextCtrl(panel, value=str(webui_defaults.get('port', '5000')))
        grid.Add(self.webui_port, 1, wx.EXPAND)

        vbox.Add(grid, 1, wx.EXPAND | wx.ALL, 15)
        vbox.Add(wx.StaticText(
            panel,
            label='TeamTalk server settings can be configured later from the WebUI.'
        ), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.btnGetKey = wx.Button(panel, label='Get Groq API Key')
        self.btnSave = wx.Button(panel, label='Save', id=wx.ID_OK)
        self.btnCancel = wx.Button(panel, label='Cancel', id=wx.ID_CANCEL)
        self.btnSave.SetDefault()
        buttons.Add(self.btnGetKey)
        buttons.AddStretchSpacer()
        buttons.Add(self.btnCancel, 0, wx.RIGHT, 5)
        buttons.Add(self.btnSave)
        vbox.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        panel.SetSizer(vbox)
        self.btnGetKey.Bind(wx.EVT_BUTTON, self.OnGetApiKey)
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.Bind(wx.EVT_CLOSE, lambda evt: self.EndModal(wx.ID_CANCEL))
        self.CenterOnParent()

    def OnGetApiKey(self, event):
        webbrowser.open('https://console.groq.com/keys')

    def OnSave(self, event):
        try:
            webui_port = int(self.webui_port.GetValue().strip())
            if not (0 < webui_port < 65536):
                raise ValueError('WebUI port out of range')
        except ValueError as e:
            wx.MessageBox(
                f'Invalid WebUI port: {e}',
                'Input Error',
                wx.OK | wx.ICON_WARNING
            )
            return

        if not self.webui_host.GetValue().strip():
            wx.MessageBox(
                'WebUI Address cannot be empty.',
                'Input Error',
                wx.OK | wx.ICON_WARNING
            )
            return

        self.config_data['language'] = self.language_choice_values[self.language.GetSelection()]
        self.config_data['webui_host'] = self.webui_host.GetValue().strip()
        self.config_data['webui_port'] = webui_port
        self.EndModal(wx.ID_OK)

    def GetConfigData(self):
        from config_manager import DEFAULT_CONFIG

        # Preserve the complete internal config structure with defaults, but
        # expose only Language + WebUI settings in this desktop dialog.
        structured_data = copy.deepcopy(DEFAULT_CONFIG)
        structured_data['Bot']['language'] = self.config_data.get(
            'language', DEFAULT_CONFIG['Bot']['language']
        )
        structured_data['WebUI'] = {
            'host': self.config_data.get('webui_host', DEFAULT_CONFIG['WebUI']['host']),
            'port': str(self.config_data.get('webui_port', DEFAULT_CONFIG['WebUI']['port'])),
            'setup_complete': 'False'
        }
        return structured_data
