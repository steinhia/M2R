function bnds2txtGrid (filetxtgrid, tiers, maxs)
%%
% Amelie 2008, modified for Berlin 09/2011
% bnds2txtGrid (filetxtgrid, tiers, maxs)
% write boundaries "bnds" into a textgrid "filetxtgrid" for Praat
% Short text format, all tiers have the same duration: from 0 to maxs sec
%
% - tiers contains the information for each of the label tiers
%   - tiers(n).name : Tiers number n name
%   - tiers(n).bnds: nboundaries * 2 matrices of interval (in sec)of the
%        boundaries in the first column and offsets in the second column
%        changed 09/2013: if one column then point tiers
%   - tiers(n).labels: cellarray of strings that countains the label of
% the boundaries
% - max : duration of the recording in sec
%
%

if nargin ~= 3
    disp('Wrong number of parameters, bnds2txtGrid:')
    help bnds2txtGrid
    return
    
end

%%
% test for the txtGrid file
%%
if exist (filetxtgrid, 'file')
    disp (sprintf('The file %s already exist, will be overwritten',...
        filetxtgrid))
end

fidtxt = fopen (filetxtgrid, 'w');
if fidtxt == -1
    error ('Failed to open txtGrid file %s', filetxtgrid)
end


ntiers =  length(tiers);

%%
% write headers for text grids file (short format)
%%
fprintf (fidtxt, 'File type = "ooTextFile"\n');
fprintf (fidtxt, 'Object class = "TextGrid"\n');
fprintf (fidtxt, '\n');
% onset time
fprintf (fidtxt, '0\n');
% offset time
fprintf (fidtxt, '%0.4f\n', maxs);
fprintf (fidtxt, '<exists>\n');
% number of intervals tiers
fprintf (fidtxt, '%d\n', ntiers);


%%
%   Process each tiers
%%

for nt = 1 : ntiers
%     disp (sprintf('Process Tier %d', nt))
     
    
    if isempty (tiers(nt).bnds) | ...
            (size(tiers(nt).bnds, 2)== 2 & ...
            ~ isempty (find((tiers(nt).bnds(:, 2)-tiers(nt).bnds(:, 1)) < 0)))
        tiers(nt).name =  [];
        tiers(nt).name =  'Empty';
        tiers(nt).bnds =  [];
        tiers(nt).bnds(1, :) =  [0 maxs];
        tiers(nt).labels =  [];
        tiers(nt).labels{1} =  'Empty';
    end
    
    if size (tiers(nt).bnds, 2) == 2
        fprintf (fidtxt, '"IntervalTier"\n');
    else
        fprintf (fidtxt, '"TextTier"\n');
    end
    % tiers name
    if strcmp (tiers(nt).name(1), '"')==1; c = ''; else; c='"';end
    fprintf (fidtxt, '%s%s%s\n',  c ,tiers(nt).name, c);
    % onset time
    fprintf (fidtxt, '0\n');
    % offset time
    fprintf (fidtxt, '%0.4f\n', maxs);
    
    % number of boundaries in current tier
    n = size(tiers(nt).bnds, 1);
    fprintf (fidtxt, '%d\n', n);
    
    % process each boundaries
    for b = 1 : (size(tiers(nt).bnds, 1))
        fprintf (fidtxt, '%0.6f\n', (tiers(nt).bnds(b, 1)));
        
        if size (tiers(nt).bnds, 2) == 2
            fprintf (fidtxt, '%0.6f\n', (tiers(nt).bnds(b, 2)));
        end

        if ~isempty(tiers(nt).labels{b})
            
            tiers(nt).labels{b} = regexprep(tiers(nt).labels{b},...
                '"+','""');
            tiers(nt).labels{b} = regexprep(tiers(nt).labels{b},...
                '"""+','""');
            
            fprintf (fidtxt, sprintf('"%s"\n', tiers(nt).labels{b}));
        else
            fprintf (fidtxt, sprintf('""\n'));
        end
        
        
    end
end

%% close file
fclose (fidtxt);


end

       
