setTimeout(function () {
    try {
        // debugger;
        var iframe = document.querySelector('iframe')
        if (iframe) {
            var slide = self.get('slide');
            self.slide = slide
            if (slide.type == "video" && slide.embedUrl && slide.embedUrl.includes('vimeo')) {
            }else{
                return;
            }

            var player = new Vimeo.Player(iframe);
            player.on('play', function () {
                console.log('Played the video');
            });
//                            player.getVideoTitle().then(function (title) {
//                                console.log('title:', title);
//                            });
//
//                            player.on('timeupdate', function (time) {
//                                console.log(time);
//                            });

            player.on('pause', function () {
                var durationTime = 0;
                var currentTime = 0;

                player.getDuration().then(function (value) {
                    durationTime = value;
                    player.getCurrentTime().then(function (value) {
                        currentTime = value;

                        if (currentTime > durationTime - 30) {
                            if (!self.slide.hasQuestion && !self.slide.completed) {
                                self.trigger_up('slide_to_complete', self.slide);

                                if (self.slide.hasNext) {
                                    setTimeout(function () {
                                        self.trigger_up('slide_go_next');

                                    }, 4000);
                                }
                            }
                        }
                    })
                })
            });
        }
    } catch (error) {
        console.log("No es un video de vimeo");
        console.log(error);
    }
}, 5000);