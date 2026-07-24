-- Shift+字母 追加辅码处理器
-- 在首音节后追加辅码字母，并把光标移到追加辅码的末尾
-- 参考 editor.lua 的补码位置定位逻辑

local rime = require "sbxlm.lib"

local this = {}

function this.init(env)
  env.last_fuzhu_pos = nil
end

---@param key_event KeyEvent
---@param env Env
function this.func(key_event, env)
  -- 只处理按下事件，带 Shift 且无其他修饰键
  if key_event:release() then
    return rime.process_results.kNoop
  end
  if not key_event:shift() then
    return rime.process_results.kNoop
  end
  if key_event:alt() or key_event:ctrl() or key_event:super() or key_event:caps() then
    return rime.process_results.kNoop
  end

  local keycode = key_event.keycode
  -- A-Z
  if keycode < 0x41 or keycode > 0x5a then
    return rime.process_results.kNoop
  end

  local context = env.engine.context
  -- 必须有候选菜单
  if not context:has_menu() then
    return rime.process_results.kNoop
  end

  -- 获取当前可编辑输入（排除已确认部分）
  local confirmed_position = context.composition:toSegmentation():get_confirmed_position()
  local previous_caret_pos = context.caret_pos
  local current_input = context.input:sub(confirmed_position + 1, previous_caret_pos)

  -- 必须满足补码条件：末音节有 3 码，且前面至少还有一个音节
  if not rime.match(current_input, ".+[bpmfdtnlgkhjqxzcsrywv][aeiou]{2}") then
    return rime.process_results.kNoop
  end

  -- 找出首音节的长度（第二个声母之前的位置）
  local first_char_code_len = current_input:find("[bpmfdtnlgkhjqxzcsrywv]", 2) - 1

  -- 把光标移到首音节末尾
  context.caret_pos = confirmed_position + first_char_code_len

  -- 插入辅码字母（小写）
  local ch = string.char(keycode + 32)
  context:push_input(ch)

  -- 光标移到追加辅码的末尾（即插入位置 + 1）
  context.caret_pos = confirmed_position + first_char_code_len + 1

  return rime.process_results.kAccepted
end

return this
