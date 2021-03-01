%% load one extracted frame
load('ZED_2020-10-29-09-14-44_extracted20.mat')
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

%% show point cloud
figure
x = point_cloud_extracted(:, :, 2);
y = point_cloud_extracted(:, :, 3);
z = point_cloud_extracted(:, :, 1);
c = reshape(point_cloud_rgb_extracted, [], 4);
scatter3(x(:), y(:), z(:), 0.1, c(:, 1:3), '.')
view(0, 0)
axis equal
axis tight

%% load all extracted frame
load('ZED_2020-10-29-09-14-44_aligned.mat')
load('CSI_2020-10-29-09-14-44_aligned.mat')

frame_num = 2;

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

% show point cloud
% figure
% x = squeeze(point_cloud(frame_num, :, :, 2));
% y = squeeze(point_cloud(frame_num, :, :, 3));
% z = squeeze(point_cloud(frame_num, :, :, 1));
% c = reshape(squeeze(point_cloud_rgb(frame_num, :, :, :)), [], 4);
% scatter3(x(:), y(:), z(:), 0.1, c(:, 1:3), '.')
% view(0, 0)
% axis equal
% axis tight

