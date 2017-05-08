// Phantomjs odoo helper
// jshint evil: true, loopfunc: true

var system = require('system');

function waitFor (condition, callback, timeout, timeoutMessageCallback) {
    timeout = timeout || 10000;
    var start = new Date();

    (function waitLoop() {
        if(new Date() - start > timeout) {
            console.log('error', timeoutMessageCallback ? timeoutMessageCallback() : "Timeout after "+timeout+" ms");
            phantom.exit(1);
        } else if (condition()) {
            callback();
        } else {
            setTimeout(waitLoop, 250);
        }
    }());
}

function waitForReady (page, ready, callback){
    waitFor(function() {
        console.log("PhantomTest: wait for condition:", ready);
        return page.evaluate(function (ready) {
            var r = false;
            try {
                console.log("page.evaluate eval expr:", ready);
                r = !!eval(ready);
            } catch(ex) {
            }
            console.log("page.evaluate eval result:", r);
            return r;
        }, ready)
    }, callback);
}

function timeoutMessage (){
    return ("Timeout\nhref: " + window.location.href +
                   "\nreferrer: " + document.referrer +
                   "\n\n" + (document.body && document.body.innerHTML)).replace(/[^a-z0-9\s~!@#$%^&*()_|+\-=?;:'",.<>\{\}\[\]\\\/]/gi, "*");
}

function PhantomTest() {
    var self = this;
    this.options = JSON.parse(system.args[system.args.length-1]);
    this.inject = this.options.inject || [];
    this.origin = 'http://localhost';
    this.origin += this.options.port ? ':' + this.options.port : '';

    // ----------------------------------------------------
    // configure phantom and page
    // ----------------------------------------------------
    this.pages = {} // sname -> page

// wrong indent to keep original code in place
for (var sname in self.options.sessions){ 
    session = self.options.sessions[sname];
    var jar = require('cookiejar').create();
    this.page = require('webpage').create();
    this.page.cookieJar = jar;
    this.pages[sname] = this.page;
    jar.addCookie({
        'domain': 'localhost',
        'name': 'session_id',
        'value': session.session_id,
    });
    this.page.viewportSize = { width: 1366, height: 768 };
    this.page.onError = function(message, trace) {
        var msg = [message];
        if (trace && trace.length) {
            msg.push.apply(msg, trace.map(function (frame) {
                var result = [' at ', frame.file, ':', frame.line];
                if (frame.function) {
                    result.push(' (in ', frame.function, ')');
                }
                return result.join('');
            }));
            msg.push('(leaf frame on top)');
        }
        console.log('error', JSON.stringify(msg.join('\n')));
        phantom.exit(1);
    };
    this.page.onAlert = function(message) {
        console.log('error', message);
        phantom.exit(1);
    };
    this.page.onConsoleMessage = function(message) {
        console.log(message);
    };

    var pagesLoaded = false;
(function(){
    // put it in function to have new variables scope
    // (self.page is changed)
    var page = self.page;
    var timeout = session.timeout ? Math.round(parseFloat(session.timeout)*1000 - 5000) : 30000;

    setTimeout(function () {
        if (pagesLoaded)
            return;
        page.evaluate(function (timeoutMessage) {
            var message = timeoutMessage();
            console.log('error', message);
        }, timeoutMessage);
        phantom.exit(1);
    }, timeout);
})()

}// for (var sname in self.options.sessions){ 


    // ----------------------------------------------------
    // run test
    // ----------------------------------------------------
    this.run = function() {
        // load pages and then call runCommands

        pages_count = 0;
        onPageReady = function(status) {
            if (status === "success") {
                pages_count--;
                if (pages_count == 0){
                    pagesLoaded = true;
                    self.runCommands()
                }
            }
        };


    // wrong indent to keep original code in place
    for (var sname in self.pages){
        page = self.pages[sname];
        session = self.options.sessions[sname];
        // authenticate
        url_path = session.url_path;
        if(session.login) {
            var qp = [];
            qp.push('db=' + self.options.db);
            qp.push('login=' + session.login);
            qp.push('key=' + session.password);
            qp.push('redirect=' + encodeURIComponent(url_path));
            url_path = "/login?" + qp.join('&');
        }
        var url = self.origin + url_path;

        // open page
        ready = session.ready || "true";

        pages_count++;
        (function(){
            var currentPage = page;
            console.log('start loading', url);
            currentPage.open(url, function(status) {
                if (status !== 'success') {
                    console.log('error', "failed to load " + url);
                    phantom.exit(1);
                } else {
                    console.log('loaded', url, status);
                    // clear localstorage leftovers
                    currentPage.evaluate(function () { localStorage.clear() });
                    // process ready
                    waitForReady(page, ready, onPageReady);
                }
            });
        })()
    }//for (var sname in self.pages){

    };

    this.runCommands = function() {
        var i = -1;
        function nextCommand(){
            i++;
            if (i == self.options.command.length){
                return;
            }
            command = self.options.command[i];
            page = self.pages[command.session];
            code = command.code || 'true';
            ready = command.ready || 'true';

            console.log("PhantomTest.runCommands: executing: " + code);
            (function(){
                var commandNum = i;
                setTimeout(function () {
                    if (commandNum != i)
                        return;
                    page.evaluate(function (timeoutMessage) {
                        var message = timeoutMessage();
                        console.log('error', message);
                    }, timeoutMessage);
                    phantom.exit(1);
                }, command.timeout || 60333)
            })()
            page.evaluate(function (code) { return eval(code); }, code);
            waitForReady(page, ready, nextCommand)
        }
    };

}

// js mode or jsfile mode
if(system.args.length === 2) {
    pt = new PhantomTest();
    pt.run();
}

// vim:et:
