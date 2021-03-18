module.exports = function(grunt) {


    // 1. All configuration goes here 
    grunt.initConfig({
	pkg: grunt.file.readJSON('package.json'),

	// Project configuration.
	uglify: {
            main: {
                files: [
                    {src: 'cc-lite-main.js', dest: 'cc-lite-main.min.js'},
                ],
            },
            globalview: {
                files: [
                    {src: 'cc-lite-global-view.js', dest: 'cc-lite-global-view.min.js'},
                ],
            },
            instview: {
                files: [
                    {src: 'cc-lite-instance-view.js', dest: 'cc-lite-instance-view.min.js'},
                ],
            },
	},

	watch: {
            main: {
                files: ['cc-lite-main.js'],
                tasks: ['uglify:main'],
                options: {
                    spawn: false,
                },
            },
            globalview: {
                files: ['cc-lite-global-view.js'],
                tasks: ['uglify:globalview'],
                options: {
                    spawn: false,
                },
            },
            instview: {
                files: ['cc-lite-instance-view.js'],
                tasks: ['uglify:instview'],
                options: {
                    spawn: false,
                },
            },
	},

	jsbeautifier : {
	    files : ['cc-lite-main.js', 
		     'cc-lite-global-view',
		     'cc-lite-instance-view.js'],
	},

	jshint: { 
	    // lint your project's server code
	    all: [ 'cc-lite-main.js', 
		     'cc-lite-global-view',
		     'cc-lite-instance-view.js'],
	}
    });

    // 3. Where we tell Grunt we plan to use this plug-in.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    //grunt.loadNpmTasks('grunt-contrib-watch');
    //grunt.loadNpmTasks("grunt-jsbeautifier");
    //grunt.loadNpmTasks('grunt-contrib-jshint');
    
    // 4. Where we tell Grunt what to do when we type "grunt" into the terminal.
    grunt.registerTask('default', ['uglify']);

};

