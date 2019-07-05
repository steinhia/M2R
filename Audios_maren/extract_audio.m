sdir=dir('*.edt');
fs      = {sdir.name};

    % process each edt file
    for f = 1:length(fs)
        % current edt file
        cf = fs{f};
        [~, fr, ~] = fileparts (cf);
        fileSnds    = [wavDest,'Audios_maren/id06/','j3','/',fr,'.wav'];
        data                =   readEDT(cf);
%         prm.metric          =   'euclidean';
%         %groupIdxs          =    kmeans2(data(:,2),2,prm);
% 
%         %find the synchro triggers without setting up
%         groupIdxs           =   kmeans(data(:,2).data,2);
%         startEndPts         =   find(diff(groupIdxs)~=0);
        newAudio1           =   data(:,1).data;
        audiowrite (fileSnds, newAudio1, sr)
    end
    