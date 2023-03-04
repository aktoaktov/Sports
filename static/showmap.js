ymaps.ready(init);

function init() {
    var selected = []

    var map = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 7
    });


    map.controls.remove('geolocationControl');
    map.controls.remove('searchControl');
    map.controls.remove('typeSelector');
    map.controls.remove('routeButton');
    map.controls.remove('trafficControl');
    map.controls.remove('fullscreenControl');
    map.controls.remove('zoomControl');
    map.controls.remove('rulerControl');

    $('*[class*="copyrights-promo" i]').remove()


    $.get(
        "/api/all",
        data => {
            data.forEach(entry => {
                placemark = new ymaps.Placemark(
                    entry[2],
                    {
                        balloonPanelMaxMapArea: 0,
                        openEmptyBalloon: true,
                        balloonContentBody: `${entry[1]}`,

                        oid: entry[0]
                    }
                )

                placemark.events.add(
                    'click', e => {
                        if (e.get("ctrlKey")) {
                            oid = e.get('target').properties.get('oid')

                            if (selected.find(v => v == oid)) {
                                e.get("target").options.set("preset", "islands#blueIcon")
                                selected = selected.filter(v => v !== oid)
                            } else {
                                e.get('target').options.set('preset', "islands#redIcon")
                                selected.push(oid)
                            }

                            $.ajax("/api/graphics", {
                                processData: false,
                                type: "POST",
                                data: JSON.stringify(selected),
                                contentType: "application/json"
                            }).done(res => {
                                $('#details').html(res)
                                // $('svg').attr('viewBox', '')
                            })

                            e.get("target").balloon.events.close()
                        } else {
                            $.get(`/api/object/${entry[0]}`, res => {
                                $('#details').html(res)
                            })
                        }
                    }
                )

                map.geoObjects.add(placemark)
            })
        }
    ).fail(
        // TODO: Какое-то предупреждение о том что что-то не так
    )
}