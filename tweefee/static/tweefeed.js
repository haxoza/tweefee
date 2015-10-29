var TweeFeed = function (host, port, wsPath, maxTweets) {
    this.url = TweeFeed.buildUrl(host, port, wsPath)
    this.$container = $('#tweefeed');
    this.twitterURL = 'https://twitter.com/';
    this.errorTimeout = 5000;
    this.maxTweets = maxTweets;
};

TweeFeed.buildUrl = function (host, port, wsPath) {
    if (port) {
        return 'ws://' + host + ':' + port + wsPath;
    }
    return 'ws://' + host + wsPath;
};

TweeFeed.prototype.init = function () {
    var socket = new WebSocket(this.url);
    var that = this;
    socket.onmessage = function (msg) {
        that.onMessage(msg);
    };
    socket.onclose = function () {
        setTimeout(function () {
            that.init()
        }, that.errorTimeout);
    }
};

TweeFeed.prototype.onMessage = function (msg) {
    var data = jQuery.parseJSON(msg.data);
    var that = this;
    data.reverse().forEach(function (value) {
        that.processTweet(value);
    });
};

TweeFeed.prototype.processTweet = function (tweet) {
    var date = new Date(tweet.date);
    var userURL = this.twitterURL + tweet.user.handle;
    var tweetURL = userURL + '/status/' + tweet.id;
    $('<div>', {class: 'tweet clear'})
        .append($('<img>', {class: 'avatar', src: tweet.user.avatar_url}))
        .append($('<div>', {class: 'name'})
            .append($('<a>', {class: 'fullname', text: tweet.user.full_name + ' ', href: userURL})
                .append($('<span>', {class: 'handle', text: '@' + tweet.user.handle})))
            .append($('<a>', {class: 'date', text: date.toLocaleString(), href: tweetURL})))
        .append($('<p>', {
            class: 'text',
            html: twttr.txt.autoLink(tweet.content, {usernameIncludeSymbol: true, urlEntities: tweet.entities.urls})
        }))
        .prependTo(this.$container);
    if (this.$container.children().length > this.maxTweets) {
        this.$container.children(':last').remove();
    }
};
