%% load one extracted frame
load('ZED_2020-11-30-02-00-08_extracted20.mat')
figure
subplot(3, 1, 1)
imagesc(depth_extracted)
axis equal
colorbar

subplot(3, 1, 2)
imshow(zed_frame_extracted(:, :, 1:3))
axis equal

subplot(3, 1, 3)
imshow(csi_frame_extracted)
axis equal


%%
load('ZED_2020-11-30-02-00-08_aligned.mat')
load('CSI_2020-11-30-02-00-08_aligned.mat')

frame_num = 20;

figure
subplot(3, 1, 1)
imagesc(squeeze(depth(frame_num, :, :)))
axis equal
colorbar

subplot(3, 1, 2)
imshow(squeeze(zed_frame(frame_num, :, :, 1:3)))
axis equal

subplot(3, 1, 3)
imshow(squeeze(csi_frame(frame_num, :, :, 1:3)))
axis equal
