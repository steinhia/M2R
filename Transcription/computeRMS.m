function [rms win] = computeRMS ( s, swin )
%
% Compute rms using Tiede function
% s = structure, s.snd: sound, s.sr: freq

% adjust this 20 ms if the result is too noisy/smooth
win = round (swin * s.sr/1000);
rms = sqrt (filtfilt(rectwin(win)/win, 1, s.sound.^2));

end
