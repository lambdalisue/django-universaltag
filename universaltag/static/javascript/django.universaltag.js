/*
 * django-universaltag Ajax JavaScript
 * 
 * @author:		Alisue <lambdalisue@hashnote.net>
 * @url:		http://hashnote.net/
 *
 * Required:
 * - jQuery over 1.3
 * - jQuery UI (Autocomplete, DragDrop)
 * 
 */
(function($){
	// Define POST, PUT, DELETE method for RESTful API
	$.extend({
		"post": function(url, data, success, error) {
			error = error || function() {};
			return $.ajax({
				"url": url,
				"data": data,
				"success": success,
				"type": "POST",
				"cache": false,
				"error": error,
				"dataType": "json"
			});
		},
		"put": function(url, data, success, error) {
			error = error || function() {};
			return $.ajax({
				"url": url,
				"data": data,
				"success": success,
				"type": "PUT",
				"cache": false,
				"error": error,
				"dataType": "json"
			});
		},
		"del": function(url, data, success, error) {
			error = error || function() {};
			return $.ajax({
				"url": url,
				"data": data,
				"success": success,
				"type": "DELETE",
				"cache": false,
				"error": error,
				"dataType": "json"
			});
		}
	});
	String.prototype.strip = function(){
		return this.replace(/^\s*(.*?)\s*$/, "$1");
	}
	// Define universalTag
	$.fn.universalTag = function(settings){
		settings = $.extend(true, {
			'suggestions': [],
			'classes': {
				'wrap':	'universaltag',
				'tag': 'tag',
				'frozen': 'frozen'
			},
			'titles': {
				'inputBox': "Press [Enter] to post.",
				'closeButton': "Close input field.",
				'openButton': "Open input field.",
				'deleteButton': "Delete this tag.",
				'freezeButtonThaw': "Thaw this tag.",
				'freezeButtonFreeze': "Freeze this tag."
			},
			'plugins': {
				'autocomplete':	true,
			},
			'tag_max_length': 50,
			'debug': true
		}, settings);
		function getApiUrl($ul){
			return $ul.attr('universaltag_api_url');
		}
		function isFreezable($ul){
			return $ul.attr('freezable') && $ul.attr('freezable') != '';
		}
		function isDeletable($tag){
			return !$tag.hasClass(settings.classes.frozen);
		}
		return this.each(function(){
			var $ul = $(this).wrap($('<div>').addClass(settings.classes.wrap));
			if (!getApiUrl($ul)){
				if (settings.debug) {
					alert("Warning: wrong ul is selected (django.universaltag.js)\n\n"+
						"`ul` doesn't have custome attribute (`universaltag_api_url`).\n"+
						"To enable the feature of editing tags, these custome attribute is reqiured.\n"+
						"Please make sure that you have configured it correctly.\n\n" +
						"(You see this message because `debug` option is set `true`)");
				}
				return false;
			}
			function factoryTag(instance, freezable){
				var $tag = $('<li>').addClass(settings.classes.tag);
				if(instance.frozen){
					$tag.addClass(settings.classes.frozen);
				}
				$tag.append($('<a>').attr('href', instance.tag.absolute_uri).text(instance.tag.label));
				$tag.append(factoryToolbox(freezable, isDeletable($tag)));
				return $tag;
			}
			function addTag($ul, labels){
				labels = labels || $('li.pencilcase div.pencilset input', $ul).val();
				$.post(getApiUrl($ul), {'labels': labels}, function(data, textStatus){
					$.each(data, function(){
						$('li.pencilcase div.pencilset input', $ul).val('');
						var $tag = factoryTag(this, isFreezable($ul)).hide();
						$('li.pencilcase', $ul).before($tag);
						$tag.show("fast");
					});
				});
			}
			function delTag($ul, $tag){
				var url = getApiUrl($ul) + $tag.text() + "/";
				$.del(url, {}, function(data, textStatus){
					$tag.hide("fast", function(){
						$(this).remove();
					});
				});
			}
			function frzTag($ul, $tag){
				var url = getApiUrl($ul) + $tag.text() + "/";
				$.put(url, {}, function(data, textStatus){
					if(data.frozen){
						$tag.addClass(settings.classes.frozen);
						$('a.button.delete', $tag).hide('fast');
					}else{
						$tag.removeClass(settings.classes.frozen);
						$('a.button.delete', $tag).show('fast');
					}
				});
			}
			function srtTag($ul, labels){
				if(typeof(labels) == 'undefined'){
					labels = "";
					$('li.tag', $ul).each(function(){
						labels += '"' + $(this).text().strip() + '", ';
					});
					labels = labels.slice(0, -2);
				}
				$.put(getApiUrl($ul), {'labels': labels});
			}
			function factoryButton(cls, title, click){
				var $button = $('<a>').addClass('button').addClass(cls);
				$button.attr('href', 'javascript:void(0);')
				$button.attr('title', title);
				$button.click(click);
				return $button;
			}
			function factoryPencilCase(){
				function openPencilSet($pencilset){
					if($pencilset.css('display') == 'none'){
						$pencilset.show('fast', function(){
							$('input', $pencilset).focus();
							$('a.button.open', $pencilset).addClass('active');
						});
					}
				}
				function closePencilSet($pencilset){
					if($pencilset.css('display') != 'none'){
						$pencilset.hide('fast', function(){
							$('div.pencilset input', $pencilset).val('');
							$('a.button.open', $pencilcase).removeClass('active');
						});
					}
				}
				function factoryPencilSet($pencilcase){
					var $pencilset = $('<div>').addClass('pencilset');
					var $inputbox = $('<input>');
					$inputbox.attr('title', settings.titles.inputBox);
					$inputbox.attr('maxlength', settings.tag_max_length);
					if(settings.plugins.autocomplete){
						if(typeof($inputbox.autocomplete) != "undefined"){
							$inputbox.autocomplete({
								'source': settings.suggestions
							});
						}
					}
					$inputbox.keydown(function(e){
						if(e.keyCode == 27){ // ESC: Cancel
							closePencilSet($pencilset);
						}else if(e.keyCode == 13){ //Return: Post
							var $ul = $(this).parents('ul.universaltag');
							addTag($ul);
						}else{
							return true;
						}
						return false;
					});
					var $closebtn = factoryButton('close', settings.titles.closeButton, function(){
						closePencilSet($pencilset);
					});
					$pencilset.append($inputbox).append($closebtn);
					$pencilset.hide();
					return $pencilset;
				}
				var $pencilcase = $('<li>').addClass('pencilcase');
				var $pencilset = factoryPencilSet($pencilcase);
				var $openbtn = factoryButton('open', settings.titles.openButton, function(){
					openPencilSet($pencilset);
				});
				
				$pencilcase.append($openbtn);
				$pencilcase.append($pencilset);
				return $pencilcase;
			}
			function factoryToolbox(freezable, deletable){
				var $toolbox = $('<div>').addClass('toolbox');
				var $deletebtn = factoryButton('delete', settings.titles.deleteButton, function(){
					var $ul = $(this).parents('ul.universaltag');
					var $tag = $(this).parents('li.tag');
					delTag($ul, $tag);
				});
				if(!deletable){
					$deletebtn.hide();
				}
				$toolbox.append($deletebtn);
				if(freezable){
					function autoSetFreezeButtonTitle($freezebtn){
						var $tag = $freezebtn.parent('li.tag');
						if($tag.hasClass('frozen')){
							$freezebtn.attr('title', settings.titles.freezeButtonThaw);
						}else{
							$freezebtn.attr('title', settings.titles.freezeButtonFreeze);
						}
						return $freezebtn;
					}
					var $freezebtn = factoryButton('freeze', '', function(){
						var $ul = $(this).parents('ul.universaltag');
						var $tag = $(this).parents('li.tag');
						frzTag($ul, $tag);
						autoSetFreezeButtonTitle($(this));
					});
					autoSetFreezeButtonTitle($freezebtn);	
					$toolbox.append($freezebtn);
				}
				return $toolbox;
			}
			$ul.append(factoryPencilCase());
			// Apply toolbox to each tags
			$('li.tag', $ul).each(function(){
				$(this).append(factoryToolbox(isFreezable($ul), isDeletable($(this))));
				
			});
			// Make to be able sort
			$ul.sortable({items:"li.tag", stop: function(){
				srtTag($ul);
			}});
		});
	};
})(jQuery);
