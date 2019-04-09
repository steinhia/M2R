function vadout=apply_vad(p1,p2)
%
%if ~exist('audiodir','var')
%  fprintf('Please specify an audio directory\n')
%  return
%end

% ---vad parameters (to tune)---
% speech noise threshold
if ~exist('p1','var')
  p1=0.05;
end
% speech region smoothing
if ~exist('p2','var')
  p2=50;
end

% set path
addpath mfiles/

fs=8000;

% ---feature---
% GT
NbCh=64;
% Gabor
nb_mod_freq=2;
% LTSV
R=50; % context
M=10; % smoothing
ltsvThr=0.5;
ltsvSlope=0.2;
% vprob2 and ltsv2
K=30; order=4;
% -------------

% ---vad model---
load('models/model.mat')


% ---visualize---
visualize=false;

for idNum=1:15
    path=sprintf('AudioList/id%d/',idNum);
    filenames=dir(strcat(path,'*.wav'));
    for k = 1 : length(filenames)
     name=filenames(k).name;
     nameMat=strcat(name(1:end-3),'mat');
     % read in audio
     [sam,fs_orig]=audioread(fullfile(path,name));
     sam_8k=downsample(sam(:,1),fs_orig/fs);

     % [1] extract cochleagram
     gt=FE_GT(sam_8k,fs,NbCh);

     % [2] Gabor filtering applied on mel
     gbf=FE_GBF(sam_8k,fs,nb_mod_freq,false);
     gbf= [gbf gbf(:,ones(1,10)*size(gbf,2))];
     gbf = gbf(:,1:size(gt,2));

     % [3] LTSV
     ltsv=FE_LTSV(sam_8k,fs,R,M,gt,ltsvThr,ltsvSlope);
     ltsv2 = convert_to_context_stream(ltsv, K, order);
     ltsv2= [ltsv2 ltsv2(:,ones(1,10)*size(ltsv,2))];
     ltsv2 = ltsv2(:,1:size(gt,2));

     % [4] vprob prob
     vprob=voicingfeature(sam_8k,fs);
     vprob2 = convert_to_context_stream(vprob, K, order);
     vprob2 = [vprob2 vprob2(:,ones(1,10)*size(vprob,2))];
     vprob2 = vprob2(:,1:size(gt,2));

     % feature for VAD
     test_x = [gt;gbf;ltsv2;vprob2];
     test_x_norm = mvn(test_x);

     % VAD decoding
     [~,~,output] = nntest(dnn, test_x_norm');
     outprob=double(output(:,1));
     vadout=medfilt1(outprob.^2,p2)>p1;
     save(strcat(path,'Mat/',nameMat),'vadout')
    %
    % if visualize
    %  imagesc(mvn(gt));axis xy;hold on;
    %  plot(10*vadout,'m','LineWidth',3); zoom xon; hold off
    % end
    end
end
