var EditStorageItemController = function ($scope, $log, $http, $modal, $modalInstance, item, title,isEdit) {

    $scope.item = item;
    $scope.title = title;
    $scope.IsEdit = isEdit;

    $scope.testConnection = function () {
        var model = JSON.stringify($scope.item);
        $http.jsonrpc('api', 'Storage.testConnection', { 'storageModel': model })
        .success(function (data, status, headers, config) {
            if (data.result) {
                $scope.item.IsActive = true;
            } else {
                if (typeof data.error !== 'undefined') {
                    alert("Failed connect:" + data.error.message);
                } else {
                    alert("Failed connect.");
                }               
            }
        }).error(function (data, status, headers, config) {
            alert("Failed connect unknown error.");
        });
    }

    $scope.ok = function () {
        $modalInstance.close($scope.item);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss();
    };
};

var DeleteStorageItemController = function ($scope, $log, $http, $modal, $modalInstance,item) {

    $scope.item = item;

    $scope.ok = function () {
        $modalInstance.close('Ok');
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
};