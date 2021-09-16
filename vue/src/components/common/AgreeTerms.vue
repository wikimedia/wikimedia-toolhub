<template>
	<I18nHtml
		class="text-caption"
		msg="agree-terms"
		:tag="tag"
	>
		<a
			href="https://wikimediafoundation.org/wiki/Terms_of_Use"
			target="_blank"
		>{{ $t( 'link-tou' ) }}</a>
		<a
			href="https://www.mediawiki.org/wiki/Code_of_Conduct"
			target="_blank"
		>{{ $t( 'link-coc' ) }}</a>
		<a
			href="https://creativecommons.org/publicdomain/zero/1.0/"
			target="_blank"
		>{{ $t( 'link-cc0' ) }}</a>
	</I18nHtml>
</template>

<script>
import I18nHtml from '@/components/common/I18nHtml';

export default {
	name: 'AgreeTerms',
	components: {
		I18nHtml
	},
	props: {
		tag: {
			type: [ String, Boolean, Object ],
			default: 'P'
		}
	}
};
</script>
