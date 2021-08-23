<template>
	<a
		v-if="isImage"
		class="inline-flex"
		target="_blank"
		:href="commonsUrl"
	>
		<v-img
			:src="imageinfo.thumburl"
			:srcset="srcset( imageinfo )"
			:height="size"
			:width="size"
			:alt="commonsUrl"
			aspect-ratio="1"
			contain
			crossorigin="anonymous"
			decoding="async"
			loading="lazy"
			referrerpolicy="origin-when-cross-origin"
		/>
	</a>
	<v-icon
		v-else
		:size="size"
		color="base20"
	>
		{{ fallback }}
	</v-icon>
</template>

<script>
import SwaggerClient from 'swagger-client';

export const FILE_RE = /^https:\/\/commons\.wikimedia\.org\/wiki\/(File:.+)$/;
export const API_URL = 'https://commons.wikimedia.org/w/api.php?';

export default {
	name: 'CommonsImage',
	props: {
		commonsUrl: {
			type: String,
			default: () => ''
		},
		fallback: {
			type: String,
			default: () => 'mdi-tools'
		},
		size: {
			type: Number,
			default: () => 100
		}
	},
	computed: {
		isImage() {
			const m = FILE_RE.exec( this.commonsUrl );
			return m !== null;
		}
	},
	asyncComputed: {
		imageinfo: {
			get() {
				const m = FILE_RE.exec( this.commonsUrl );
				if ( m !== null ) {
					const params = [
						[ 'action', 'query' ],
						[ 'prop', 'imageinfo' ],
						[ 'iiprop', 'url' ],
						[ 'format', 'json' ],
						[ 'utf8', 1 ],
						[ 'formatversion', 2 ],
						[ 'smaxage', 86400 ],
						[ 'maxage', 86400 ],
						[ 'origin', '*' ],
						[ 'titles', m[ 1 ] ],
						[ 'iiurlwidth', this.size ],
						[ 'iiurlheight', this.size ]
					];
					const qs = new URLSearchParams( params );
					const req = {
						method: 'GET',
						url: API_URL + qs.toString()
					};
					return SwaggerClient.http( req ).then( ( { body } ) => {
						return body.query.pages[ 0 ].imageinfo[ 0 ];
					} );
				}
			},
			default: {}
		}
	},
	methods: {
		srcset( imginfo ) {
			if ( imginfo && 'responsiveUrls' in imginfo ) {
				return Object.keys( imginfo.responsiveUrls ).map(
					( k ) => imginfo.responsiveUrls[ k ] + ' ' + k + 'x'
				).join();
			}
			return '';
		}
	}
};
</script>
