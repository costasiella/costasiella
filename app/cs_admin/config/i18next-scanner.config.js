var fs = require('fs');
var chalk = require('chalk');

module.exports = {
    options: {
        src: [
            'src/**/*.{html,js,jsx}',
            // Use ! to filter out files or directories
            '!src/**/*.spec.{js,jsx}',
            '!src/i18n/**',
            // '!test/**',
            '!**/node_modules/**'
        ],
        dest: './src/i18n',
        debug: false,
        removeUnusedKeys: true,
        sort: false,
        func: {
            list: ['i18next.t', 'i18n.t', 't'],
            extensions: ['.js', '.jsx']
        },
        trans: {
            component: 'Trans',
            i18nKey: 'i18nKey',
            defaultsKey: 'defaults',
            extensions: ['.js', '.jsx'],
            fallbackKey: function(ns, value) {
                // Returns a hash value as the fallback key
                return sha1(value);
            }
        },
        lngs: [
            'en_US',
            'nl_NL'
        ],
        ns: [
            'common'
        ],
        defaultLng: 'en_US',
        defaultNs: 'common',
        defaultValue: '__STRING_NOT_TRANSLATED__',
        resource: {
            // the load path is relative to current working directory
            loadPath: '../src/i18n/{{lng}}/{{ns}}.json',
            // the save path is relative to the output path
            savePath: 'i18n/{{lng}}/{{ns}}.json',
            jsonIndent: 4,
            lineEnding: '\n'
        },
        nsSeparator: ':', // namespace separator
        keySeparator: '.', // key separator
        interpolation: {
            prefix: '{{',
            suffix: '}}'
        }
    },
    transform: function customTransform(file, enc, done) {
        "use strict";
        const parser = this.parser;
        const content = fs.readFileSync(file.path, enc);
        let count = 0;

        parser.parseFuncFromString(content, { list: ['i18next._', 'i18next.__'] }, (key, options) => {
            parser.set(key, Object.assign({}, options, {
                nsSeparator: false,
                keySeparator: false
            }));
            ++count;
        });

        if (count > 0) {
            console.log(`i18next-scanner: count=${chalk.cyan(count)}, file=${chalk.yellow(JSON.stringify(file.relative))}`);
        }

        done();
    }
};
