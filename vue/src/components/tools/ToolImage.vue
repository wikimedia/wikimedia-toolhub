<template>
	<CommonsImage
		v-bind="$attrs"
		:commons-url="tool.icon"
		:fallback="fallbackIcon"
	/>
</template>

<script>
import CommonsImage from '@/components/common/CommonsImage';

export default {
	name: 'ToolImage',
	components: {
		CommonsImage
	},
	props: {
		tool: {
			type: Object,
			required: true
		}
	},
	computed: {
		fallbackIcon() {
			switch ( this.tool.tool_type ) {
				case 'web app':
					return 'mdi-web';
				case 'desktop app':
					return 'mdi-monitor';
				case 'bot':
					return 'mdi-robot-outline';
				case 'gadget':
					return 'mdi-file-code-outline';
				case 'user script':
					return 'mdi-script-text-outline';
				case 'command line tool':
					return 'mdi-console';
				case 'coding framework':
					return 'mdi-archive-outline';
				case 'lua module':
					return 'mdi-language-lua';
				case 'template':
					return 'mdi-iframe-braces-outline';
				default:
					return 'mdi-tools';
			}
		}
	}
};
</script>
