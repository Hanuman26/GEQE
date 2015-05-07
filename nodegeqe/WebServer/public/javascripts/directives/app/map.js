angular.module('NodeWebBase')
    .controller('mapController',['$scope','$rootScope','shapeService','markerService',function($scope, $rootScope, shapeService, markerService){
        $rootScope.$on('themeChanged', function (event) {
            if($rootScope.theme.mapStyles){
                $scope.map.setOptions({styles: $rootScope.theme.mapStyles});
            }
            else
                $scope.map.setOptions({styles: null});

            if($rootScope.theme.shapeStyles){
                $scope.drawingManager.setOptions({
                    polygonOptions:$rootScope.theme.shapeStyles,
                    rectangleOptions:$rootScope.theme.shapeStyles
                });

                angular.forEach($scope.shapes,function(shape){
                    shape.setOptions($rootScope.theme.shapeStyles);
                });
            }
        });

        $scope.kmlControl = function() {
            var controlDiv = document.createElement('div');
            controlDiv.index = 1;
            $scope.map.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(controlDiv);

            // Set CSS for the control border
            var controlUI = document.createElement('div');
            controlUI.style.backgroundColor = '#fff';
            controlUI.style.border = '2px solid #fff';
            controlUI.style.borderRadius = '3px';
            controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
            controlUI.style.cursor = 'pointer';
            controlUI.style.marginBottom = '22px';
            controlUI.style.textAlign = 'center';
            controlUI.title = 'Click to load kml';
            controlDiv.appendChild(controlUI);

            // Set CSS for the control interior
            var controlText = document.createElement('div');
            controlText.style.color = 'rgb(25,25,25)';
            controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
            controlText.style.fontSize = '16px';
            controlText.style.lineHeight = '38px';
            controlText.style.paddingLeft = '5px';
            controlText.style.paddingRight = '5px';
            controlText.innerHTML = 'kml';
            controlUI.appendChild(controlText);

            google.maps.event.addDomListener(controlUI, 'click', function() {
                var fileSelector = $('<input type="file" />');

                fileSelector.change(function(evt){
                    $scope.renderKmlFile(evt.target.files[0]);
                });
                fileSelector.click();

            });

        };

        $scope.renderKmlFile = function(file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var kml = e.target.result;

                var myParser = new geoXML3.parser({map: $scope.map});
                myParser.parseKmlString(kml);
            };
            reader.readAsText(file);
        };

        $scope.init = function() {

            $scope.kmlControl();

            shapeService.init($scope.map, $scope.drawingManager);
            markerService.init($scope.map);
        }

    }])
    .directive('map',function ($rootScope) {
        function link(scope, element, attrs) {
            $(document).ready(function () {
                var myLatlng = new google.maps.LatLng(41.495753190958816,-81.70090198516846);
                var mapOptions = {
                    zoom: 10,
                    center: myLatlng
                };

                if($rootScope.theme.mapStyles){
                    mapOptions.styles = $rootScope.theme.mapStyles;
                }

                scope.map = new google.maps.Map(element[0], mapOptions);

                scope.drawingManager = new google.maps.drawing.DrawingManager({
                    drawingControl: true,
                    drawingControlOptions: {
                        position: google.maps.ControlPosition.TOP_CENTER,
                        drawingModes: [
                            google.maps.drawing.OverlayType.POLYGON,
                            google.maps.drawing.OverlayType.RECTANGLE
                        ]
                    },
                    polygonOptions:$rootScope.theme.shapeStyles,
                    rectangleOptions:$rootScope.theme.shapeStyles
                });

                scope.drawingManager.setMap(scope.map);

                scope.init();
            });
        }
        return {
            restrict: 'AE',
            link: link
        };
    });