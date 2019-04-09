function [interSounds, thr] = detectVoiced (rms, threshold, nb)
%% Amelie 27 Sept 2011
% to detect main periods with speech in a file
% return a n*2 tables with the interval boundaries (samples number)
%
% signal    : wav to analyse
% sr        : sampling rate
% threshold : value beyong which signal will be considered as voiced try .01
%             but should be adapted to the needs
% rmsWindow: in msec, usually 20 but but it much greater to get groups
%               instead of vowel, should be adapted to the needs
% required computeRMS.m, provided by Mark Tiede

ntr = 1;

if ~ isempty (nb) & length(threshold)>1
    ntr = length (threshold);
end


n = nb;
thr = threshold(1);
for i = 1 : ntr
    disp (sprintf ('Trying threshold %f', threshold(i)))
    %% 
    voiced              = find(rms > threshold(i));
    d                   = diff(voiced);
    idEndVoiced         = [find( d > 1); length(voiced)];
    idOnsVoiced         = [1; idEndVoiced(1:end-1)+1 ];
    interSounds         = [ voiced(idOnsVoiced) voiced(idEndVoiced)];
    pInterSounds        = interSounds;
    disp (sprintf ('n expected %d, n found %d', nb, size(interSounds, 1)))
    if size(interSounds, 1) == n
        thr = threshold(i); break;
    end
    
    
end


end

%% plot to test
% clf;
% subplot(2, 1, 1)
% plot(signal)
% for i = 1 : size(interSounds, 1)
%     line([interSounds(i, 1) interSounds(i, 1)], [-.1 .2], 'color', 'r')
%     line([interSounds(i, 2) interSounds(i, 2)], [-.1 .2], 'color', 'r')
% end
%
%
% subplot(2, 1, 2)
% plot(rms)
% for i = 1 : size(interSounds, 1)
%     line([interSounds(i, 1) interSounds(i, 1)], [-.1 .2], 'color', 'r')
%     line([interSounds(i, 2) interSounds(i, 2)], [-.1 .2], 'color', 'r')
% end


