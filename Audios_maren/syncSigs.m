function newAudio= syncSigs(wavFile,edtFile,initialDelay)

[audioSig,audioSr]=audioread(wavFile);
[data,hdr,h] = ReadEDT(edtFile);
prm.metric='euclidean';
groupIdxs = kmeans2(data(:,2),2,prm);
% groupIdxs = kmeans(data(:,2),2);
startEndPts=find(diff(groupIdxs)~=0);
newAudio=data(startEndPts(1):startEndPts(2),:);
newAudio=newAudio(initialDelay.*audioSr:end,:);

newAudio=interp1([1:length(newAudio)],newAudio,linspace(1,length(newAudio),length(audioSig)));