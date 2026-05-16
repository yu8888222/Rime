local M = {}

local function current_code(context)
  local segmentation = context.composition:toSegmentation()
  local segment = segmentation and segmentation:back() or nil
  if not segment then
    return context.input
  end
  if segment._end <= segment.start then
    return ""
  end
  return context.input:sub(segment.start + 1, segment._end)
end

function M.init(env)
  local config = env.engine.schema.config
  env.name_space = env.name_space:gsub("^*", "")
  env.seen = {}
  env.last_code = ""
end

function M.tags_match(segment, env)
  local context = env.engine.context
  if context.caret_pos ~= context.input:len() then
    return false
  end
  if not context:get_option("exclude_seen_single") then
    return false
  end
  if segment:has_tag("reverse_moqima") or segment:has_tag("radical_flypy") then
    return false
  end
  if segment:has_tag("emojis") or segment:has_tag("easy_en_simp") or segment:has_tag("add_user_dict") then
    return false
  end
  return true
end

function M.func(translation, env)
  local context = env.engine.context
  local code = current_code(context) or ""
  if code == "" then
    env.seen = {}
    env.last_code = ""
    for cand in translation:iter() do
      yield(cand)
    end
    return
  end

  local last_code = env.last_code or ""
  if last_code == "" then
    env.seen = {}
  elseif #code < #last_code then
    env.seen = {}
  elseif code:sub(1, #last_code) ~= last_code then
    env.seen = {}
  end
  env.last_code = code

  local code_len = #code
  local recorded_first = false

  for cand in translation:iter() do
    local text = cand.text
    local seen_len = text and env.seen[text] or nil
    if seen_len and seen_len < code_len then
      goto continue
    end

    yield(cand)
    if not recorded_first and text then
      local old = env.seen[text]
      if not old or old > code_len then
        env.seen[text] = code_len
      end
      recorded_first = true
    end

    ::continue::
  end
end

return M
