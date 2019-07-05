function channel = readEDT(filename)
% =========================================================================
% Read a EDT file into the struct channel. channel(i).time is the time vector,
% channel(i).data contents the data. Additional informations are stored in the 
% scructure
%
%
% Einlesen einer EDT-Datei in die Struct channel. channel(i).time ist der
% Zeitvektor, channel(i).data sind die Daten. Sonstige Informationen werden
% ebenfalls in der Struct abgelegt.
%
% readEDT - Einlesen von EDASWin-Dateien in Matlab
% Copyright (C) 2009 Patrick Seiniger, Bundesanstalt für Straßenwesen,
% Germany - www.bast.de
%
% This program is free software; you can redistribute it and/or modify it
% under the terms of the GNU General Public License as published 
% by the Free Software Foundation; either version 3 of the License, or 
% any later version.
% 
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of 
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
% See the GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License 
% along with this program; if not, see http://www.gnu.org/licenses/.

% =========================================================================
% Header einlesen
% =========================================================================

% Datei öffnen
ha = fopen(filename);

% Wo beginnt der Header?

% Byte 8ff vom Anfang gezählt enthält die Information Header-Beginn
fseek(ha,8,'bof');
var_HeaderOffset = fread(ha,1,'uint32');

% Header ist in Klartext vorhanden, also müssen wir keine Binäroperationen
% durchführen

% Vorspulen und gesamten Header als Array of Cellstrings einlesen:
fseek(ha,var_HeaderOffset,'bof');
inhalt = [];
while ~feof(ha)
    inhalt{end+1} = fgets(ha);
end
% in Inhalt steht nun der komplette Header (allgemeiner und 
% kanalspezifischer Teil)

% Anfang Allgemeinheader:
pos_Header = find(strncmp(inhalt,'beginheader:',length('beginheader:')));

% Anfang der Channelheaders:
pos_Channelheader = find(strncmp(inhalt,'beginchannel:',length('beginchannel:')));
nr_Channels = length(pos_Channelheader);

% Aus dem globalen Header relevante Einstellungen
% einlesen

% Bereiche der einzelnen Kanäle identifizieren
for i = 1:nr_Channels-1
    channel(i).bereich_Header = pos_Channelheader(i):pos_Channelheader(i+1);
end
channel(nr_Channels).bereich_Header = pos_Channelheader(end):length(inhalt);
    
% Welche Felder sollen eingelesen werden?
felder = [{'channel_offset'} {'typ'} {'org'} {'frames'} {'clk'} {'starttime'} {'unit'} {'ampli'} {'offset'} {'ylow'} {'yhigh'} {'minscale'} ...
    {'minscale'} {'maxscale'} {'name'} {'pchan'}];

bereich_global = 1:pos_Channelheader(1)-1;

% Felder können im globalen oder in den kanalspezifischen Headern definiert
% sein. Vorgehensweise also: erst den globalen Header auswerten, wenn das
% jeweilige Feld nicht definiert ist, dann wird es leer gelassen. Danach
% der Reihe nach die Kanäle abarbeiten und anders gesetzte Felder
% überschreiben.

% erst alle gesuchten Felder aus dem jeweiligen Kanalheader auslesen
for i = 1:nr_Channels    
    for k = 1:length(felder);
        channel(i).(felder{k}) = getKey([felder{k} ':'],bereich_global,inhalt);
    end
end

% jetzt einzelne Kanalheader durchgehen
for i = 1:nr_Channels
    for k = 1:length(felder);
        temp = getKey([felder{k} ':'],channel(i).bereich_Header,inhalt);
        if ~isempty(temp)
            channel(i).(felder{k}) = temp;
        end
        clear temp;
    end
end
% Header vollständig

% =========================================================================
% Daten einlesen
% =========================================================================

% Daten einlesen
% Beginn der Daten ist immer 32
pos_BeginData = 32;

% Länge der einzelnen Kanäle herausfinden (steht in Frames)
for i = 1:nr_Channels
    if strcmp(channel(i).org{1},'linear')
        laenge(i) = str2num(channel(i).frames{1});
    else
        laenge(i) = str2num(channel(i).org{1}(6:end));
    end
    channel(i).data = [];
end

% Zurückspulen und Daten einlesen

fseek(ha,pos_BeginData,'bof');
i = 1;

% Solange der Dateipositionszeiger noch nicht beim Headerbeginn angekommen
% ist, wechselweise die Kanaldaten einlesen
while ftell(ha)<var_HeaderOffset
%     daten = fread(ha,laenge(i),channel(i).typ{1});
daten = fread(ha,laenge(i),channel(i).typ{1});
    daten = daten * str2num(channel(i).ampli{1}) + str2num(channel(i).offset{1});
    channel(i).data = [channel(i).data; daten];
    
    i = i +1;
    if i > nr_Channels
        i = 1;
    end
end

% Zeitvektor für die einzelnen Kanäle definieren
for i = 1:nr_Channels
    channel(i).time = (0:length(channel(i).data)-1).*str2num(channel(i).clk{1});
end

% Datei schließen
fclose(ha);

% fertig.

function inhalt_Key = getKey(name,bereich,inhalt)
% function inhalt_Key = getKey(name,bereich,inhalt)


wo = find(strncmp(inhalt(bereich),name,length(name)));
if length(wo) >0
    temp = deblank(inhalt{bereich(wo)});
    inhalt_Key = {temp(length(name)+1:end)};
else inhalt_Key = [];
end

