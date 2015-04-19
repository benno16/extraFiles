var modStorageApp = angular.module('modStorageApp', ['angular-json-rpc', 'ui.grid', 'ui.grid.edit', 'ui.grid.resizeColumns', 'tableSort', 'modStorageFilters', 'ui.bootstrap']);

modStorageApp.controller('MainController', function ($scope, $http, $modal,$log) {

        $scope.name = "Demo";

        $scope.GridDef = [
                { field: 'Name' },
                { field: 'dummy', cellTemplate: '<div><button type="button" ng-click="editItem()"  class="btn btn-primary btn-xs">Edit</button></div>' }
        ];

        $scope.Storages = [];

        $scope.newStorage = function () {
            var modalInstance = $modal.open({
                templateUrl: '/static/Dialogs/CreateEditStorageItemDialog.html',
                controller: EditStorageItemController,
                windowClass: 'mHeadCreate roundHead',
                resolve: {
                    item: function () {
                        return {
                            ID: '',
                            Name: 'New item',
                            Type: '',
                            UserName: '',
                            Password: '',
                            Path: '',
                            IsActive: false,
                            LastError: ''
                        }
                    },
                    title: function () {
                        return 'Create storage item'
                    },
                    isEdit: function () {
                        return false;
                    }
                }
            });

            modalInstance.result.then(function (item) {
                var model = JSON.stringify(item);
                $http.jsonrpc('api', 'Storage.createStorage', { 'storageModel': model })
	            .success(function (data, status, headers, config) {
	                if (data.result) {
	                    item.ID = data.result;
	                    $scope.Storages.push(item);
	                    LoadData();
	                } else {
	                    alert("Failed to save the item:" + data.error.message);
	                }
	            }).error(function (data, status, headers, config) {
	                alert("Failed to save the item");
	            });
            }, function () {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        $scope.editItem = function (item) {
            var backup = angular.copy(item);

            var modalInstance = $modal.open({
                templateUrl: '/static/Dialogs/CreateEditStorageItemDialog.html',
                controller: EditStorageItemController,
                windowClass: 'mHeadEdit roundHead',
                resolve: {
                    item: function () {
                        return item;
                    },
                    title: function () {
                        return 'Edit storage item'
                    },
                    isEdit: function () {
                        return true;
                    }
                }
            });

            modalInstance.result.then(function (item) {
                var model = JSON.stringify(item);
                $http.jsonrpc('api', 'Storage.updateStorage', { 'storageModel': model })
	            .success(function (data, status, headers, config) {
	                if (!data.result) {
	                    alert("Failed to save the item:" + data.error.message);
	                }
	            }).error(function (data, status, headers, config) {
	                alert("Failed to save the item");
	            });
            }, function () {
                item.Name = backup.Name;
                item.Path = backup.Path;
                item.UserName = backup.UserName;
                item.Password = backup.Password;
                item.IsActive = backup.IsActive;
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        $scope.deleteItem = function (item) {
            var modalInstance = $modal.open({
                templateUrl: '/static/Dialogs/AreYouSureYouWantToDelete.html',
                controller: DeleteStorageItemController,
                windowClass: 'mError roundHead',
                resolve: {
                    item: function () {
                        return item;
                    }
                }
            });

            modalInstance.result.then(function () {
                $http.jsonrpc('api', 'Storage.deleteStorage', { 'itemId': item.ID })
	            .success(function (data, status, headers, config) {
	                if (data.result) {
	                    var index = $scope.Storages.indexOf(item);
	                    $scope.Storages.splice(index, 1);  	                    
	                } else {
	                    alert("Failed to delete the item:" + data.error.message);
	                }
	            }).error(function (data, status, headers, config) {
	                alert("Failed to delete the item");
	            });
            }, function () {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        LoadData = function () {
            //url, method, parameters, config
            $http.jsonrpc('api', 'Storage.getStorages')
	        .success(function (data, status, headers, config) {
	            $scope.name = "Awsom";	            
	            $scope.Storages = data.result;
	        }).error(function (data, status, headers, config) {
	            $scope.name = "Darn";
	        });
        };

        $scope.TestSubmit = function () {
            if ($scope.Storages.length > 0) {
                var model = JSON.stringify($scope.Storages[0]);
                $http.jsonrpc('api', 'Storage.updateStorage', { 'storageModel': model })
	        .success(function (data, status, headers, config) {
	            $scope.name = "Submit completed";
	            alert(data.result);
	        }).error(function (data, status, headers, config) {
	            $scope.name = "Darn";
	        });
            }
        };

        LoadData();

    });

modStorageApp.controller('modVizXController', function ($scope, $http, $modal, $log) {

    $scope.ApiAddress = '';

    LoadConfiguration = function () {
        //url, method, parameters, config
        $http.jsonrpc('api', 'ModVizX2.loadConfiguration')
        .success(function (data, status, headers, config) {
            $scope.ApiAddress = data.result;            
        }).error(function (data, status, headers, config) {
            
        });
    };

    $scope.SaveConfiguration = function () {
        $http.jsonrpc('api', 'ModVizX2.saveConfiguration', { 'config': $scope.ApiAddress })
	    .success(function (data, status, headers, config) {
	        if (data.result) {
	            alert('Configuration saved.');
	        } else {
	            alert('An error occured.');
	        }	        
	    }).error(function (data, status, headers, config) {
	        alert('An unexpected error occured.');
	    });
    };

    LoadConfiguration();
});

angular.module('modStorageFilters', []).filter('checkmark', function () {
    return function (input) {
        return input ? '\u2713' : '\u2718';
    };
});