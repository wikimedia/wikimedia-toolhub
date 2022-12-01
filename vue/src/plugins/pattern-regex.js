import i18n from '@/plugins/i18n';

export const patternRegexList = [
	{
		pattern: '^[-\\w]+$',
		description: i18n.t( 'tooltitle-pattern-regex' )
	},
	{
		pattern: '^https://commons\\.wikimedia\\.org/wiki/File:.+\\..+$',
		description: i18n.t( 'toolicon-pattern-regex' )
	},
	{
		pattern: '^(x-.*|[A-Za-z]{2,3}(-.*)?)$',
		description: i18n.t( 'tooluilangs-pattern-regex' )
	},
	{
		pattern: '^(\\*|(.*)?\\.?(mediawiki|wiktionary|wiki(pedia|quote|books|source|news|versity|data|voyage|media))\\.org)$',
		description: i18n.t( 'toolforwikis-pattern-regex' )
	}
];

export function patternRegexRule( exp ) {
	const expRgx = new RegExp( exp );
	let expDesc = '';

	for ( const pr in patternRegexList ) {
		const item = patternRegexList[ pr ];
		const prRgx = new RegExp( item.pattern );

		if ( expRgx.toString() === prRgx.toString() ) {
			expDesc = item.description;
			break;
		}
	}

	return [
		( v ) => ( !v || '' ) ? true : expRgx.test( v ) || expDesc
	];
}

export default patternRegexRule;
