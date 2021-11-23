<template>
	<dl class="row ma-0">
		<dt class="me-1">{{ label }}</dt>
		<!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
		<dd v-if="required">*</dd>
	</dl>
</template>

<script>
export default {
	name: 'InputLabel',
	props: {
		label: {
			type: String,
			required: true
		},
		required: {
			type: Boolean
		}
	}
};
</script>
