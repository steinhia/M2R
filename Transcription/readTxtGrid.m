function tiers = readTxtGrid (fileGrid)
%%
%
%   Melie Mai 2008, extended to read multiple tiers files, sept 2011
%
%   readTxtGrid :
%   read multiple tiers TextGrid written in short format
%
%   fileGrid is the name of the text grid file
%
%   return tiers with :
%
%       - tiers(n).bnds: nboudaries * 2 matrices, column 1: time onset,
%                           column 2: time offset
%       - change on 9/2013 to integrate point tiers
%       - tiers(n).name: tiers name
%       - tiers(n).labels: cell of string with nbnds labels
%
%  suppose that the file is written in the right format
%

tiers = [];

fid = fopen( fileGrid, 'r' );
if fid == -1
    error ( sprintf('Failed opening file %s', fileGrid))
end

%%
%   Get the number of tiers
%%

while (1); 
d = fgetl(fid);
if strcmp(d, '<exists>') | d == -1
break; 
end
end


if d == -1
    error ('TxtGrid file %s is not well formed', fileGrid)
end

ntiers          = str2num (fgetl(fid));

nt              = 1;

%%
%   Process each interval tier
%%
% find a interval tiers

while 1

    l = fgetl(fid);
    while (~strcmp(l, '"IntervalTier"') & ~strcmp(l, '"TextTier"') & l~=-1)
         l = fgetl(fid);
    end
    if l == -1
        break;
    end
    if strcmp(l, '"IntervalTier"')
       t = 1;
    else
       t = 2;
    end
    tiers(nt).bnds  = [];
    
    %% find an interval tiers
    % read the name of tier
    tiers(nt).name   = fgetl(fid);
    
    
    % ignore onset, offset times
    fgetl(fid); fgetl(fid);
    
    % number of boundaries to read
    nbnds            = str2num(fgetl(fid));
    
    % next line is the name of the first boundaries
    % read each boundary
    for b = 1 : nbnds
        % onset, offset
        onset = str2num(fgetl(fid));
        
        if t == 1
            offset = str2num(fgetl(fid));
            tiers(nt).bnds = [tiers(nt).bnds ; [onset offset]];
        else
            tiers(nt).bnds = [tiers(nt).bnds ; onset];
        end
        % label of boundaries
        lab = fgetl(fid);
        if strcmp (lab, '""')
            tiers(nt).labels{b} = '';
        else lab = lab(2:end-1);
            tiers(nt).labels{b} = lab;
        end
        
    end
    
    
    nt = nt + 1;
    if nt > ntiers; break; end
        
    
    
end

fclose (fid);



end