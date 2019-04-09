
% crée un nouveau fichier text grid pour chaque fichier
cd ~/Documents/Alex/Transcription/
lDir=dir('AudioList');
dirFlags = [lDir.isdir];
f=lDir(dirFlags);
% on parcourt chaque id
for i=1:15
    % on parcourt chaque fichier à découper
    idFold=strcat(strcat('AudioList/id',num2str(i)),'/');
    lDir=dir(idFold);
    for j=1:length(lDir)
        if ~lDir(j).isdir
            audioName=lDir(j).name;
            createTG(idFold,audioName,i);
        end
    end
end

function txtG=createTG(idFold,audioname,idNum)
    %ouvre le fichier audio
    [y,Fs]=audioread(strcat(idFold,audioname));
    newFs=5000;
    aud=y(:,1);
    aud2=resample(aud,newFs,Fs);
    %plot(ltime,aud2);
    s.sound=aud2;
    s.sr=newFs;
    %swin=1.0/10%200*Fs/1000;
    swin2=500;
    [rms win]=computeRMS(s,swin2);
    %ltime=linspace(0,(length(aud2)-1)/1000,length(aud2));
    %ltimeRMS=linspace(0,(length(aud2)-1)/1000,length(rms));
    %clf;
    %hold on 
    %plot(ltime,aud2)
    %plot(ltimeRMS,rms,'r')
    [interSounds,thr]=detectVoiced(rms,0.02,80);
    for i=1:length(interSounds)
        for j=1:2
            interSounds(i,j)=interSounds(i,j)/1000;
        end
    end
    n=length(interSounds);
    struct.name='transcription';
    struct.labels=repmat({'a'},n,1);
    struct.bnds=interSounds;
    maxs=length(y)/Fs;
    txtGridPath=strcat('AudioList/id',num2str(idNum),'/');
    txtGridName=strcat(audioname(1:end-4),'.txtGrid');
    bnds2txtGrid(strcat(txtGridPath,txtGridName),struct,maxs);
end


