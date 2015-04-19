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

var CreateImageController = function ($scope, $log, $http, $modal, $modalInstance, item) {

    $scope.item = item;
    
	$scope.Sourcedrives = ['/dev/sda','/dev/sdb'];

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
	
	
	$scope.Storages = [{"ID":1,"Name":"100TB","Path":"//serverb/data"},
						{"ID":2,"Name":"250TB","Path":"//nas/data"}]
	
	$scope.treedata = [
        {
            "Name": "User", "Path": "role1", "Children": [
              { "Name": "subUser1", "Path": "role11", "Children": [] },
              {
                  "Name": "subUser2", "Path": "role12", "Children": [
                    {
                        "Name": "subUser2-1", "Path": "role121", "Children": [
                          { "Name": "subUser2-1-1", "Path": "role1211", "Children": [] },
                          { "Name": "subUser2-1-2", "Path": "role1212", "Children": [] }
                        ]
                    }
                  ]
              }
            ]
        },
        { "Name": "Admin", "Path": "role2", "Children": [] },
        { "Name": "Guest", "Path": "role3", "Children": [] }
    ];

	/*
    $http.get('/api/folderroot').then(function (result) {
        var rData = result.data;

        $.each(rData, function (index, element) {
            element.LoadChildData = LoadChildDataImpl;
        });

        $scope.treedata = result.data;
    });*/

    function LoadChildDataImpl(element) {
        $.each(element.Children, function (index, child) {
            if (child.LoadChildData === undefined) {
                child.LoadChildData = LoadChildDataImpl;
                $http.post('/api/getfolders', child.Path).then(function (result) {
                    child.Children = result.data;
                });
            }
        });
    };

    $scope.ok = function () {
        $modalInstance.close($scope.item);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss();
    };
};


